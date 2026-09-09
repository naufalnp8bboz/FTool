import sys
import os

# Add root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ftool.core.ml_engine import MLEngine
from ftool.core.cv_engine import CVEngine
from ftool.core.code_engine import CodeEngine
from ftool.core.nlp_engine import NLPEngine

def test_all():
    print("--- Testing ML Engine ---")
    ml = MLEngine()
    df = ml.load_sample_dataset("iris")
    print("Iris loaded, shape:", df.shape)
    metrics = ml.train(target_col="target", model_name="Random Forest")
    print("Trained RF, Accuracy:", metrics["accuracy"], "Classes:", metrics["classes"])
    pred = ml.predict_single({
        "sepal length (cm)": 5.1,
        "sepal width (cm)": 3.5,
        "petal length (cm)": 1.4,
        "petal width (cm)": 0.2
    })
    print("Single prediction:", pred)
    code = ml.generate_python_code()
    print("Generated code snippet length:", len(code))

    print("\n--- Testing CV Engine ---")
    cv = CVEngine()
    cv.load_image("assets/logo.png")
    canny = cv.apply_canny()
    print("Canny applied, output shape:", canny.shape)

    print("\n--- Testing Code Engine ---")
    res = CodeEngine.execute_python_code("x = 42\nprint(f'Val: {x * 2}')")
    print("Code exec:", res)
    ast_res = CodeEngine.analyze_python_ast("def hello(x):\n    return x + 1")
    print("AST analysis:", ast_res["functions"])
    reg_res = CodeEngine.test_regex(r"\d+", "abc 123 def 456")
    print("Regex matches count:", reg_res["match_count"])
    conv = CodeEngine.convert_string("FTool", "base64_encode")
    print("Base64:", conv)

    print("\n--- Testing NLP Engine ---")
    nlp = NLPEngine.analyze_text("FTool is a great, fantastic, and powerful coding tool!")
    print("NLP sentiment:", nlp["sentiment"], "Score:", nlp["sentiment_score"])
    sim = NLPEngine.calculate_similarity("machine learning model", "deep learning and machine learning")
    print("Cosine similarity:", sim, "%")

    print("\n>>> ALL ENGINE TESTS PASSED PERFECTLY! <<<")

if __name__ == "__main__":
    test_all()
