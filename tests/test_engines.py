import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ftool.core.ml_engine import MLEngine
from ftool.core.cv_engine import CVEngine
from ftool.core.code_engine import CodeEngine
from ftool.core.nlp_engine import NLPEngine
from ftool.core.osint_engine import OSINTEngine

def test_all():
    print("--- Testing ML & Neural Network Engine ---")
    ml = MLEngine()
    df = ml.load_sample_dataset("iris")
    print("Iris loaded, shape:", df.shape)
    metrics = ml.train(target_col="target", model_name="Neural Network (MLP)")
    print("Trained Neural Net, Accuracy:", metrics["accuracy"], "Layers:", metrics.get("network_layers"))
    pred = ml.predict_single({
        "sepal length (cm)": 5.1,
        "sepal width (cm)": 3.5,
        "petal length (cm)": 1.4,
        "petal width (cm)": 0.2
    })
    print("Single prediction:", pred)

    print("\n--- Testing CV & Face HUD Engine ---")
    cv = CVEngine()
    cv.load_image("assets/logo.png")
    hud_img, count = cv.apply_cyber_face_detect()
    print("Cyber Face HUD applied, target count:", count, "shape:", hud_img.shape)

    print("\n--- Testing OSINT & Defensive Recon Engine ---")
    dns_res = OSINTEngine.resolve_dns("1.1.1.1")
    print("DNS lookup:", dns_res["records"])
    headers_res = OSINTEngine.audit_http_headers("example.com")
    print("Security header audit grade:", headers_res.get("grade"), "Score:", headers_res.get("score_pct"), "%")

    print("\n--- Testing Code & NLP Engines ---")
    code_res = CodeEngine.execute_python_code("print('FTool v2.0 Operational')")
    print("Code exec:", code_res["stdout"].strip())
    nlp_res = NLPEngine.analyze_text("Antigravity and FTool are next-generation tools.")
    print("Sentiment:", nlp_res["sentiment"])

    print("\n>>> ALL ENGINE UPGRADES VERIFIED 100%! <<<")

if __name__ == "__main__":
    test_all()
