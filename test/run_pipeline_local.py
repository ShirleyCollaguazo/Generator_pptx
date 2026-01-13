from app.services.generator import run_pipeline

if __name__ == "__main__":
    out = run_pipeline(
        pdf_path="data/Computer.pdf",
        output_path="outputs/test_microserviceIngles.pptx"
    )
    print("OK:", out)
