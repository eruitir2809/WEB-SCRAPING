from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from concurrent.futures import ThreadPoolExecutor
import re
import multiprocessing


template = (
    "Tu tarea es responder específicamente a la siguiente pregunta: {parse_description}, "
    "basándote únicamente en el siguiente contenido de texto:\n\n"
    "{dom_content}\n\n"
    "Sigue cuidadosamente estas instrucciones:\n"
    "1. **Extraer Información:** Responde únicamente la información que coincida directamente con la descripción.\n"
    "2. **SIN CONTENIDO ADICIONAL:** No incluyas ningún texto adicional, comentarios ni explicaciones en tu respuesta, no incluyas nada que se encuentre entre <think> y </think>."
    "3. Prohibido el razonamiento: No incluyas pensamientos, razonamientos ni explicaciones internas, aunque creas que ayudan a justificar la respuesta."
    "4. SI NO HAY COINCIDENCIAS: Responde únicamente con 'NO HAY INFORMACIÓN RELEVANTE'."

)

model = OllamaLLM(model="DeepSeek-R1:14b")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def parse_chunk(chunk, parse_description):
    return chain.invoke({
        "dom_content": chunk,
        "parse_description": parse_description,
    })

def parse_with_ollama(dom_chunks, parse_description, max_workers=None):
    if max_workers is None:
        max_workers = min(32, multiprocessing.cpu_count() * 4)  # Escalable

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(parse_chunk, chunk, parse_description)
            for chunk in dom_chunks
        ]
        parsed_results = [f.result() for f in futures]

    return "\n".join(r for r in parsed_results if r.strip())  # Elimina vacíos

def delete_thoughts(texto):
    return re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL).strip()
