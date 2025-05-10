from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from concurrent.futures import ThreadPoolExecutor

template = (
    "Tu tarea es extraer información específica del siguiente contenido de texto: {dom_content}. "
    "Sigue cuidadosamente estas instrucciones:\n\n"
    "1. **Extraer Información:** Extrae únicamente la información que coincida directamente con la siguiente descripción: {parse_description}. "
    "2. **Sin Contenido Adicional:** No incluyas ningún texto adicional, comentarios ni explicaciones en tu respuesta. "
    "3. **Respuesta Vacía:** Si no hay información que coincida con la descripción, devuelve una cadena vacía (''). "
    "4. **Solo Datos Solicitados:** Tu salida debe contener únicamente los datos explícitamente solicitados, sin ningún otro texto."
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

