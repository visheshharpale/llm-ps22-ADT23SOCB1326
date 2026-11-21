"""Run the generator on 5 sample inputs (for the testing section + screenshots).
Usage: python test_samples.py
"""
from llm import generate_flashcards

SAMPLES = {
    "Photosynthesis": "Photosynthesis converts light energy into chemical energy in chloroplasts. The light reactions make ATP and NADPH in the thylakoids, and the Calvin cycle in the stroma fixes CO2 into glucose.",
    "Newton's laws": "Newton's first law says an object stays at rest or in uniform motion unless acted on by a force. The second law states F = ma. The third law says every action has an equal and opposite reaction.",
    "TCP vs UDP": "TCP is connection-oriented, reliable and ordered, using a three-way handshake. UDP is connectionless, faster, and has no delivery guarantee. TCP is used for web and email; UDP for video streaming and DNS.",
    "World War I": "World War I began in 1914 after the assassination of Archduke Franz Ferdinand. The Allies included France, Britain and Russia; the Central Powers included Germany and Austria-Hungary. The war ended in 1918 and the Treaty of Versailles followed in 1919.",
    "Supervised learning": "Supervised learning trains a model on labelled data. Classification predicts categories, while regression predicts continuous values. Overfitting happens when a model memorises training data and performs poorly on new data.",
}

for name, text in SAMPLES.items():
    print(f"\n=== {name} ===")
    try:
        print(generate_flashcards(text, 4, "medium").to_string())
    except Exception as e:
        print("FAILED:", e)