from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from concurrent.futures import ThreadPoolExecutor

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

model = OllamaLLM(model="mistral")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def parse_chunk(chunk, parse_description):
    return chain.invoke({
        "dom_content": chunk,
        "parse_description": parse_description,
    })

import multiprocessing

def parse_with_ollama(dom_chunks, parse_description, max_workers=None):
    if max_workers is None:
        max_workers = min(32, multiprocessing.cpu_count() * 2)  # Escalable

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(parse_chunk, chunk, parse_description)
            for chunk in dom_chunks
        ]
        parsed_results = [f.result() for f in futures]

    return "\n".join(r for r in parsed_results if r.strip())  # Elimina vacíos

