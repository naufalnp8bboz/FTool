import socket
import ssl
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List

class OSINTEngine:
    TARGET_PLATFORMS = [
        {"name": "GitHub", "url": "https://github.com/{}", "check_type": "status"},
        {"name": "Reddit", "url": "https://www.reddit.com/user/{}/about.json", "check_type": "status"},
        {"name": "GitLab", "url": "https://gitlab.com/{}", "check_type": "status"},
        {"name": "Dev.to", "url": "https://dev.to/{}", "check_type": "status"},
        {"name": "DockerHub", "url": "https://hub.docker.com/v2/users/{}/", "check_type": "status"},
        {"name": "HackerNews", "url": "https://hacker-news.firebaseio.com/v0/user/{}.json", "check_type": "content"},
        {"name": "Medium", "url": "https://medium.com/@{}", "check_type": "status"},
        {"name": "Pinterest", "url": "https://www.pinterest.com/{}/", "check_type": "status"},
    ]

    @staticmethod
    def check_username(username: str) -> List[Dict[str, Any]]:
        """Passive public profile availability verification across developer & social sites."""
        results = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FTool/2.0"}
        
        for p in OSINTEngine.TARGET_PLATFORMS:
            url = p["url"].format(username)
            try:
                resp = requests.get(url, headers=headers, timeout=4, allow_redirects=True)
                exists = False
                if p["check_type"] == "status":
                    exists = (resp.status_code == 200)
                elif p["check_type"] == "content":
                    exists = (resp.status_code == 200 and resp.text.strip() != "null")

                results.append({
                    "platform": p["name"],
                    "url": url,
                    "exists": exists,
                    "status_code": resp.status_code
                })
            except Exception:
                results.append({
                    "platform": p["name"],
                    "url": url,
                    "exists": False,
                    "status_code": 0
                })
        return results

    @staticmethod
    def audit_http_headers(target_url: str) -> Dict[str, Any]:
        """Audits defensive security headers and computes a posture grade (A+ to F)."""
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        try:
            resp = requests.get(target_url, timeout=6, allow_redirects=True)
            headers = {k.lower(): v for k, v in resp.headers.items()}

            checks = [
                {
                    "header": "Strict-Transport-Security",
                    "present": "strict-transport-security" in headers,
                    "value": headers.get("strict-transport-security", "Missing"),
                    "importance": "High",
                    "description": "Enforces HTTPS connections and prevents SSL-stripping attacks."
                },
                {
                    "header": "Content-Security-Policy",
                    "present": "content-security-policy" in headers,
                    "value": headers.get("content-security-policy", "Missing")[:80] + "..." if "content-security-policy" in headers else "Missing",
                    "importance": "Critical",
                    "description": "Restricts sources of executable scripts, mitigating Cross-Site Scripting (XSS)."
                },
                {
                    "header": "X-Frame-Options",
                    "present": "x-frame-options" in headers,
                    "value": headers.get("x-frame-options", "Missing"),
                    "importance": "High",
                    "description": "Prevents clickjacking by controlling if site can be embedded in iframes."
                },
                {
                    "header": "X-Content-Type-Options",
                    "present": "x-content-type-options" in headers,
                    "value": headers.get("x-content-type-options", "Missing"),
                    "importance": "Medium",
                    "description": "Prevents MIME-type sniffing by web browsers."
                },
                {
                    "header": "Referrer-Policy",
                    "present": "referrer-policy" in headers,
                    "value": headers.get("referrer-policy", "Missing"),
                    "importance": "Medium",
                    "description": "Protects user privacy by restricting referrer header data sent on outbound links."
                },
                {
                    "header": "Permissions-Policy",
                    "present": "permissions-policy" in headers,
                    "value": headers.get("permissions-policy", "Missing")[:60] + "..." if "permissions-policy" in headers else "Missing",
                    "importance": "Low",
                    "description": "Controls browser features like geolocation, microphone, and camera."
                }
            ]

            present_count = sum(1 for c in checks if c["present"])
            score_pct = int((present_count / len(checks)) * 100)

            if score_pct >= 85:
                grade = "A+"
            elif score_pct >= 66:
                grade = "A"
            elif score_pct >= 50:
                grade = "B"
            elif score_pct >= 33:
                grade = "C"
            elif score_pct > 0:
                grade = "D"
            else:
                grade = "F"

            return {
                "success": True,
                "url": target_url,
                "status_code": resp.status_code,
                "server": headers.get("server", "Hidden / Not Disclosed"),
                "grade": grade,
                "score_pct": score_pct,
                "checks": checks,
                "raw_headers": dict(resp.headers)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "checks": []}

    @staticmethod
    def inspect_ssl(hostname: str) -> Dict[str, Any]:
        """Inspects TLS/SSL certificate status and expiration."""
        hostname = hostname.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
        ctx = ssl.create_default_context()
        try:
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()

                    subject = dict(x[0] for x in cert.get("subject", ()))
                    issuer = dict(x[0] for x in cert.get("issuer", ()))
                    
                    not_after_str = cert.get("notAfter", "")
                    expire_date = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z") if not_after_str else None
                    days_left = (expire_date - datetime.utcnow()).days if expire_date else 0

                    return {
                        "success": True,
                        "hostname": hostname,
                        "common_name": subject.get("commonName", ""),
                        "issuer_org": issuer.get("organizationName", issuer.get("commonName", "Unknown")),
                        "valid_until": not_after_str,
                        "days_remaining": days_left,
                        "tls_version": version,
                        "cipher": cipher[0] if cipher else "",
                        "is_valid": days_left > 0
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def resolve_dns(domain: str) -> Dict[str, Any]:
        """Resolves basic DNS records using system socket."""
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        records = {}
        try:
            # IPv4
            ip_list = socket.gethostbyname_ex(domain)[2]
            records["A (IPv4)"] = ip_list
        except Exception as e:
            records["A (IPv4)"] = [f"Lookup failed: {e}"]

        try:
            # Canonical Name / Host
            canonical = socket.getfqdn(domain)
            records["Canonical FQDN"] = [canonical]
        except Exception:
            records["Canonical FQDN"] = []

        return {
            "domain": domain,
            "records": records
        }

    @staticmethod
    def get_ip_info(query: str) -> Dict[str, Any]:
        """Passive public IP geolocation and ASN data."""
        clean = query.replace("https://", "").replace("http://", "").split("/")[0]
        try:
            # Resolve domain to IP if domain provided
            ip = socket.gethostbyname(clean)
            resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=4)
            data = resp.json()
            if data.get("status") == "success":
                return {
                    "success": True,
                    "ip": data.get("query", ip),
                    "country": data.get("country", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "region": data.get("regionName", "Unknown"),
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "asn": data.get("as", "Unknown"),
                    "timezone": data.get("timezone", "Unknown")
                }
            else:
                return {"success": True, "ip": ip, "country": "Resolved Locally", "city": "-", "isp": "-"}
        except Exception as e:
            return {"success": False, "error": str(e)}
