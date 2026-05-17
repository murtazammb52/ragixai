"""Quick import smoke test for evaluation dependencies."""
import sys, os
sys.path.insert(0, ".")
os.chdir("D:/code/ragixai")

print("RAGAS imports...", flush=True)
from ragas.metrics._faithfulness import faithfulness
from ragas.metrics._answer_relevance import answer_relevancy
from ragas.metrics._context_precision import context_precision
from ragas.metrics._context_recall import context_recall
from ragas.metrics._answer_correctness import answer_correctness
import ragas
print(f"ragas {ragas.__version__}: all 5 metrics OK", flush=True)
print(f"  faithfulness name     : {faithfulness.name}", flush=True)
print(f"  answer_relevancy name : {answer_relevancy.name}", flush=True)
print(f"  context_precision name: {context_precision.name}", flush=True)
print(f"  context_recall name   : {context_recall.name}", flush=True)
print(f"  answer_correctness name:{answer_correctness.name}", flush=True)

print("\nLangChain Ollama...", flush=True)
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
print("langchain_community LLM + embeddings: OK", flush=True)

print("\nOllama ping...", flush=True)
import ollama
r = ollama.generate(model="llama3.2", prompt="Say OK", options={"num_predict": 3})
print(f"Ollama: {r['response'].strip()}", flush=True)

print("\nALL CHECKS PASSED", flush=True)
