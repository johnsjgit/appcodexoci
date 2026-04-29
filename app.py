import os
import random
import time
import uuid
from datetime import datetime, timezone

import oracledb
from flask import Flask, jsonify, render_template, request


DB_USER = os.getenv("AIQUIZ_DB_USER", "ADMIN")
DB_PASSWORD = os.getenv("AIQUIZ_DB_PASSWORD")
DB_DSN = os.getenv(
    "AIQUIZ_DB_DSN",
    "(description=(retry_count=20)(retry_delay=3)"
    "(address=(protocol=tcps)(port=1521)(host=aiquizdb.adb.us-chicago-1.oraclecloud.com))"
    "(connect_data=(service_name=g1cde62092a80c9_aiquizdb_tp.adb.oraclecloud.com))"
    "(security=(ssl_server_dn_match=no)))",
)

QUESTIONS = [
    {"id": 1, "category": "OCI AI", "difficulty": "Fácil", "question": "Qué servicio de OCI se usa para invocar modelos generativos administrados?", "options": ["OCI Generative AI", "OCI DNS", "OCI Vault", "OCI WAF"], "answer": 0, "explanation": "OCI Generative AI permite usar modelos fundacionales administrados mediante API."},
    {"id": 2, "category": "ML", "difficulty": "Fácil", "question": "Qué es un prompt en IA generativa?", "options": ["Una instrucción al modelo", "Un bloque de red", "Una llave SSH", "Un backup"], "answer": 0, "explanation": "El prompt es la entrada que guía la respuesta del modelo."},
    {"id": 3, "category": "OCI AI", "difficulty": "Fácil", "question": "Qué servicio ayuda a extraer texto y campos de documentos?", "options": ["Document Understanding", "Object Events", "Data Safe", "VCN Flow Logs"], "answer": 0, "explanation": "OCI Document Understanding analiza documentos y extrae texto, tablas y pares clave-valor."},
    {"id": 4, "category": "Vector", "difficulty": "Media", "question": "Para qué sirve un embedding?", "options": ["Representar significado como vector", "Cifrar discos", "Abrir un puerto", "Crear un usuario IAM"], "answer": 0, "explanation": "Un embedding codifica texto, imagen u otro dato en un vector comparable por similitud."},
    {"id": 5, "category": "RAG", "difficulty": "Media", "question": "Qué combina RAG?", "options": ["Recuperacion y generación", "DNS y balanceo", "VPN y FastConnect", "CPU y memoria"], "answer": 0, "explanation": "RAG recupera contexto de fuentes externas y lo usa para generar respuestas mejor fundamentadas."},
    {"id": 6, "category": "Seguridad", "difficulty": "Media", "question": "Qué reduce el riesgo de alucinaciones en una app GenAI?", "options": ["Grounding con fuentes", "Más colores en UI", "Menos logs", "IP pública"], "answer": 0, "explanation": "Usar contexto recuperado y fuentes verificables reduce respuestas inventadas."},
    {"id": 7, "category": "OCI", "difficulty": "Fácil", "question": "Donde se guardan objetos como datasets, PDFs o imágenes en OCI?", "options": ["Object Storage", "IAM Policy", "Route Table", "Fault Domain"], "answer": 0, "explanation": "Object Storage es el servicio de almacenamiento de objetos de OCI."},
    {"id": 8, "category": "OCI AI", "difficulty": "Media", "question": "Qué servicio permite crear y desplegar modelos de ML en notebooks y jobs?", "options": ["OCI Data Science", "OCI Email Delivery", "OCI Health Checks", "OCI Bastion"], "answer": 0, "explanation": "OCI Data Science ofrece notebooks, jobs, modelos y despliegues para ML."},
    {"id": 9, "category": "Certificacion", "difficulty": "Fácil", "question": "Que principio IAM se recomienda aplicar siempre?", "options": ["Menor privilegio", "Acceso total global", "Usuarios compartidos", "Sin grupos"], "answer": 0, "explanation": "El menor privilegio limita permisos a lo estrictamente necesario."},
    {"id": 10, "category": "Networking", "difficulty": "Media", "question": "Qué recurso OCI controla rutas dentro de una VCN?", "options": ["Route Table", "Dynamic Group", "Vault Key", "Compartment"], "answer": 0, "explanation": "Las route tables definen el siguiente salto para el tráfico de subnets."},
    {"id": 11, "category": "AI", "difficulty": "Fácil", "question": "Qué significa LLM?", "options": ["Large Language Model", "Low Latency Machine", "Local Load Manager", "Linux Log Monitor"], "answer": 0, "explanation": "LLM es un modelo grande de lenguaje entrenado en grandes corpus."},
    {"id": 12, "category": "RAG", "difficulty": "Difícil", "question": "Que métrica suele usarse para buscar vectores similares?", "options": ["Cosine similarity", "MTU", "TTL", "Checksum"], "answer": 0, "explanation": "La similitud coseno compara dirección entre vectores, común en búsquedas semánticas."},
    {"id": 13, "category": "Database", "difficulty": "Media", "question": "Que base OCI soporta AI Vector Search en versiones modernas?", "options": ["Oracle Database", "OCI DNS", "OCI Logging", "OCI Queue"], "answer": 0, "explanation": "Oracle Database 23ai incorpora capacidades vectoriales para busqueda semántica."},
    {"id": 14, "category": "GenAI", "difficulty": "Media", "question": "Qué es temperatura en generación de texto?", "options": ["Control de aleatoriedad", "Uso de CPU", "Tamaño de subnet", "Puerto TLS"], "answer": 0, "explanation": "Temperatura mas alta aumenta variedad; mas baja hace respuestas mas deterministas."},
    {"id": 15, "category": "OCI AI", "difficulty": "Fácil", "question": "Qué servicio puede convertir voz a texto?", "options": ["OCI Speech", "OCI Vault", "OCI NAT Gateway", "OCI Budgets"], "answer": 0, "explanation": "OCI Speech provee transcripción y capacidades relacionadas con audio."},
    {"id": 16, "category": "Visión", "difficulty": "Fácil", "question": "Qué servicio detecta objetos en imágenes?", "options": ["OCI Visión", "OCI Audit", "OCI Events", "OCI DNS"], "answer": 0, "explanation": "OCI Visión analiza imágenes para clasificación, detección y OCR."},
    {"id": 17, "category": "MLOps", "difficulty": "Media", "question": "Qué problema resuelve un model catalog?", "options": ["Versionar modelos", "Asignar IPs", "Crear VCNs", "Rotar claves SSH"], "answer": 0, "explanation": "Un catalogo permite registrar, versionar y gobernar modelos."},
    {"id": 18, "category": "Responsible AI", "difficulty": "Media", "question": "Qué práctica ayuda a proteger datos sensibles en prompts?", "options": ["Enmascarar PII", "Usar HTTP", "Compartir claves", "Desactivar logs"], "answer": 0, "explanation": "Enmascarar o eliminar PII reduce exposición de datos personales."},
    {"id": 19, "category": "GenAI", "difficulty": "Difícil", "question": "Qué es fine-tuning?", "options": ["Ajustar un modelo con datos propios", "Crear una subnet", "Subir un backup", "Cambiar DNS"], "answer": 0, "explanation": "Fine-tuning adapta un modelo base a un dominio o tarea con datos adicionales."},
    {"id": 20, "category": "RAG", "difficulty": "Difícil", "question": "Qué mejora un reranker en RAG?", "options": ["Orden de documentos recuperados", "Velocidad del disco", "Cifrado de red", "Tamaño de VCN"], "answer": 0, "explanation": "Un reranker reordena candidatos para entregar el contexto mas relevante al LLM."},
    {"id": 21, "category": "OCI Cert", "difficulty": "Media", "question": "Qué recurso agrupa recursos OCI para control de acceso y costos?", "options": ["Compartment", "Shape", "Image", "VNIC"], "answer": 0, "explanation": "Los compartments organizan recursos y sirven como frontera de políticas."},
    {"id": 22, "category": "Compute", "difficulty": "Fácil", "question": "Qué es un shape en OCI Compute?", "options": ["Perfil de CPU y memoria", "Una política IAM", "Un bucket", "Un prompt"], "answer": 0, "explanation": "El shape define recursos de computo como OCPU, memoria y red."},
    {"id": 23, "category": "Networking", "difficulty": "Media", "question": "Qué permite acceso saliente a internet desde una subnet privada?", "options": ["NAT Gateway", "Local Peering", "Security Zone", "Vault"], "answer": 0, "explanation": "NAT Gateway permite salida a internet sin IP pública en las instancias."},
    {"id": 24, "category": "Security", "difficulty": "Media", "question": "Qué servicio OCI administra secretos y llaves?", "options": ["Vault", "Streaming", "Data Flow", "Resource Manager"], "answer": 0, "explanation": "OCI Vault gestiona llaves de cifrado y secretos."},
    {"id": 25, "category": "AI", "difficulty": "Media", "question": "Qué es tokenizacion?", "options": ["Dividir texto en unidades", "Abrir un firewall", "Crear un backup", "Medir latencia"], "answer": 0, "explanation": "Los modelos procesan texto en tokens, no necesariamente palabras completas."},
    {"id": 26, "category": "LLM", "difficulty": "Media", "question": "Qué indica una ventana de contexto?", "options": ["Cantidad de tokens que procesa", "Tamaño del disco", "Número de regiónes", "Tiempo de backup"], "answer": 0, "explanation": "La ventana de contexto limita entrada y salida que el modelo puede considerar."},
    {"id": 27, "category": "GenAI", "difficulty": "Difícil", "question": "Qué técnica fuerza salida con estructura JSON?", "options": ["Structured output", "Round robin", "CIDR matching", "Block volume"], "answer": 0, "explanation": "Structured output o JSON schema ayuda a obtener respuestas parseables."},
    {"id": 28, "category": "RAG", "difficulty": "Media", "question": "Qué se debe hacer antes de indexar documentos largos?", "options": ["Dividir en chunks", "Apagar la DB", "Cambiar región", "Crear un VCN"], "answer": 0, "explanation": "Chunking divide documentos para recuperar fragmentos relevantes."},
    {"id": 29, "category": "OCI AI", "difficulty": "Fácil", "question": "Qué servicio ejecuta flujos Spark administrados?", "options": ["OCI Data Flow", "OCI Vault", "OCI DNS", "OCI Bastion"], "answer": 0, "explanation": "OCI Data Flow ejecuta trabajos Apache Spark serverless."},
    {"id": 30, "category": "Observability", "difficulty": "Fácil", "question": "Qué servicio centraliza logs en OCI?", "options": ["OCI Logging", "OCI Visión", "OCI Queue", "OCI Email"], "answer": 0, "explanation": "OCI Logging recopila y consulta logs de servicios y aplicaciones."},
    {"id": 31, "category": "AI", "difficulty": "Difícil", "question": "Qué mide precisión en clasificación?", "options": ["Aciertos positivos sobre predichos positivos", "Bytes por segundo", "Uso de memoria", "Errores DNS"], "answer": 0, "explanation": "Precision mide que proporcion de positivos predichos fueron correctos."},
    {"id": 32, "category": "AI", "difficulty": "Difícil", "question": "Qué mide recall?", "options": ["Positivos encontrados sobre positivos reales", "Costo mensual", "Latencia de red", "OCPU libre"], "answer": 0, "explanation": "Recall mide cuantos positivos reales fueron detectados."},
    {"id": 33, "category": "Responsible AI", "difficulty": "Media", "question": "Qué riesgo describe sesgo en IA?", "options": ["Resultados injustos por datos", "Más ancho de banda", "Menos backups", "IP duplicada"], "answer": 0, "explanation": "Sesgo puede producir resultados desbalanceados por datos o diseño."},
    {"id": 34, "category": "LLM", "difficulty": "Media", "question": "Qué es una alucinacion?", "options": ["Respuesta falsa convincente", "Error de subnet", "Corte de energia", "Backup fallido"], "answer": 0, "explanation": "Una alucinacion es contenido incorrecto presentado con confianza."},
    {"id": 35, "category": "OCI Cert", "difficulty": "Media", "question": "Qué recurso limita tráfico a nivel subnet?", "options": ["Security List", "Tenancy", "Image", "Tag Namespace"], "answer": 0, "explanation": "Security Lists aplican reglas de red a las VNICs de una subnet."},
    {"id": 36, "category": "OCI Cert", "difficulty": "Media", "question": "Qué recurso limita tráfico a nivel VNIC/grupo?", "options": ["Network Security Group", "Object Lifecycle", "Vault Secret", "Budget"], "answer": 0, "explanation": "NSG agrupa VNICs y aplica reglas de seguridad granular."},
    {"id": 37, "category": "Database", "difficulty": "Fácil", "question": "Qué significa ATP en Autonomous Database?", "options": ["Autonomous Transaction Processing", "Automatic Token Parser", "Advanced Traffic Policy", "AI Training Pool"], "answer": 0, "explanation": "ATP es el workload transaccional de Autonomous Database."},
    {"id": 38, "category": "Database", "difficulty": "Media", "question": "Qué ventaja clave tiene Autonomous Database?", "options": ["Automatiza parches y tuning", "Requiere mas administracion", "No cifra datos", "Solo corre local"], "answer": 0, "explanation": "ADB automatiza administracion, parches, backups y optimizacion."},
    {"id": 39, "category": "GenAI", "difficulty": "Difícil", "question": "Qué es prompt injection?", "options": ["Entrada que intenta cambiar instrucciones", "Copia de backup", "Puerto bloqueado", "Función SQL"], "answer": 0, "explanation": "Prompt injection intenta manipular instrucciones o extraer datos no permitidos."},
    {"id": 40, "category": "Security", "difficulty": "Difícil", "question": "Cómo se mitiga prompt injection en RAG?", "options": ["Aislar instrucciones y filtrar fuentes", "Publicar secrets", "Desactivar IAM", "Usar cualquier HTML"], "answer": 0, "explanation": "Separar instrucciones del contenido recuperado y validar fuentes reduce el riesgo."},
    {"id": 41, "category": "OCI AI", "difficulty": "Media", "question": "Qué servicio puede traducir texto?", "options": ["OCI Language", "OCI Compute", "OCI File Storage", "OCI WAF"], "answer": 0, "explanation": "OCI Language incluye capacidades de lenguaje natural como traduccion y análisis."},
    {"id": 42, "category": "AI", "difficulty": "Fácil", "question": "Qué es clasificación supervisada?", "options": ["Aprender con etiquetas", "Aprender sin datos", "Crear rutas", "Cifrar llaves"], "answer": 0, "explanation": "En aprendizaje supervisado el modelo aprende con ejemplos etiquetados."},
    {"id": 43, "category": "AI", "difficulty": "Media", "question": "Qué es overfitting?", "options": ["Memorizar datos de entrenamiento", "Tener poca CPU", "Fallar DNS", "Usar TLS"], "answer": 0, "explanation": "Overfitting ocurre cuando el modelo no generaliza bien a nuevos datos."},
    {"id": 44, "category": "AI", "difficulty": "Media", "question": "Qué conjunto evalua el modelo durante desarrollo?", "options": ["Validacion", "VCN", "Bucket", "Wallet"], "answer": 0, "explanation": "El conjunto de validación ayuda a ajustar y comparar modelos sin tocar test final."},
    {"id": 45, "category": "AI", "difficulty": "Media", "question": "Qué representa F1-score?", "options": ["Media armónica de precisión y recall", "Uso de memoria", "Costo por token", "Número de regiónes"], "answer": 0, "explanation": "F1 balancea precisión y recall en una sola métrica."},
    {"id": 46, "category": "OCI Cert", "difficulty": "Fácil", "question": "Qué es una tenancy?", "options": ["Cuenta raiz de OCI", "Una tabla SQL", "Una ruta estática", "Un dataset"], "answer": 0, "explanation": "La tenancy es el contenedor principal de recursos OCI de una organizacion."},
    {"id": 47, "category": "OCI Cert", "difficulty": "Media", "question": "Que usa OCI para autorizar recursos dinámicamente?", "options": ["Dynamic Groups", "Public IPs", "Boot Volumes", "Images"], "answer": 0, "explanation": "Dynamic Groups permiten que recursos actúen como principales en políticas IAM."},
    {"id": 48, "category": "AI App", "difficulty": "Difícil", "question": "Qué conviene registrar en una app GenAI productiva?", "options": ["Prompt, version y respuesta", "Solo color de boton", "Nada de auditoría", "Claves privadas"], "answer": 0, "explanation": "Trazabilidad ayuda a auditar calidad, costos y comportamiento."},
    {"id": 49, "category": "AI App", "difficulty": "Media", "question": "Que limita costos en uso de LLM?", "options": ["Cuotas y máximo de tokens", "Más réplicas", "IP fija", "Menos índices"], "answer": 0, "explanation": "Limitar tokens, requests y cuotas evita consumo inesperado."},
    {"id": 50, "category": "Database", "difficulty": "Difícil", "question": "Que tipo de índice acelera busqueda semántica?", "options": ["Índice vectorial", "Índice bitmap siempre", "Índice DNS", "Índice de ruta"], "answer": 0, "explanation": "Los índices vectoriales aceleran búsquedas por similitud en embeddings."},
    {"id": 51, "category": "OCI AI", "difficulty": "Media", "question": "Qué hace OCI Anomaly Detection?", "options": ["Detecta patrones anormales", "Crea usuarios", "Asigna CIDR", "Compila Java"], "answer": 0, "explanation": "Anomaly Detection identifica comportamientos inusuales en series temporales."},
    {"id": 52, "category": "Data", "difficulty": "Media", "question": "Qué servicio integra y transforma datos visualmente?", "options": ["OCI Data Integration", "OCI Bastion", "OCI Vault", "OCI DNS"], "answer": 0, "explanation": "Data Integration permite crear pipelines de integracion y transformacion."},
    {"id": 53, "category": "Architecture", "difficulty": "Difícil", "question": "Qué patrón desacopla productor y consumidor?", "options": ["Queue o Streaming", "Security List", "Image", "Shape"], "answer": 0, "explanation": "Colas y streams desacoplan componentes y amortiguan picos."},
    {"id": 54, "category": "GenAI", "difficulty": "Media", "question": "Qué es top-p sampling?", "options": ["Muestreo por masa acumulada", "Backup incremental", "Regla de firewall", "Índice SQL"], "answer": 0, "explanation": "Top-p selecciona tokens desde un subconjunto cuya probabilidad acumulada supera p."},
    {"id": 55, "category": "AI", "difficulty": "Difícil", "question": "Qué es distillation?", "options": ["Entrenar modelo pequeño desde uno grande", "Crear volumen", "Rotar DNS", "Borrar logs"], "answer": 0, "explanation": "La destilacion transfiere conocimiento de un modelo grande a otro mas pequeño."},
    {"id": 56, "category": "OCI Cert", "difficulty": "Media", "question": "Qué gateway conecta una VCN con otra red mediante IPSec?", "options": ["DRG", "Service Gateway", "NAT Gateway", "Internet Gateway"], "answer": 0, "explanation": "Dynamic Routing Gateway conecta VCNs con redes on-premises o remotas."},
    {"id": 57, "category": "Security", "difficulty": "Media", "question": "Qué se debe evitar en repositorios de código?", "options": ["Secretos en texto plano", "README", "Pruebas", "Versionado"], "answer": 0, "explanation": "Los secretos deben almacenarse en gestores seguros, no en código."},
    {"id": 58, "category": "AI", "difficulty": "Media", "question": "Qué es inferencia?", "options": ["Usar un modelo para predecir", "Entrenar desde cero", "Crear una VCN", "Hacer backup"], "answer": 0, "explanation": "Inferencia es ejecutar el modelo para producir una salida."},
    {"id": 59, "category": "OCI AI", "difficulty": "Difícil", "question": "Qué conviene usar para invocar APIs OCI desde una instancia sin keys?", "options": ["Instance principal", "Usuario compartido", "Archivo público", "Puerto 80"], "answer": 0, "explanation": "Instance principals autentican recursos OCI mediante dynamic groups y políticas."},
    {"id": 60, "category": "Demo", "difficulty": "Fácil", "question": "En esta demo, donde se guardan los puntajes?", "options": ["Autonomous Database", "Solo navegador", "Archivo de texto", "DNS"], "answer": 0, "explanation": "La aplicación guarda los resultados en la tabla AI_QUIZ_SCORES de ATP."}
]

# Active question bank: general Artificial Intelligence only.
QUESTIONS = [
    {"id": 1, "category": "Fundamentos", "difficulty": "Fácil", "question": "Qué es inteligencia artificial?", "options": ["Sistemas que realizan tareas que requieren inteligencia", "Solo robots físicos", "Una base de datos", "Un lenguaje de estilos"], "answer": 0, "explanation": "La IA busca crear sistemas capaces de razonar, aprender, percibir o actuar en tareas complejas."},
    {"id": 2, "category": "Machine Learning", "difficulty": "Fácil", "question": "Qué es machine learning?", "options": ["Aprendizaje desde datos", "Programación sin variables", "Un tipo de cable", "Una regla de firewall"], "answer": 0, "explanation": "Machine learning permite que un sistema aprenda patrones a partir de datos."},
    {"id": 3, "category": "Deep Learning", "difficulty": "Fácil", "question": "Qué utiliza deep learning como bloque principal?", "options": ["Redes neuronales profundas", "Tablas HTML", "Índices DNS", "Discos externos"], "answer": 0, "explanation": "Deep learning usa redes neuronales con múltiples capas para aprender representaciones complejas."},
    {"id": 4, "category": "IA Generativa", "difficulty": "Fácil", "question": "Qué hace la IA generativa?", "options": ["Crea contenido nuevo", "Solo comprime archivos", "Repara cables", "Asigna direcciónes IP"], "answer": 0, "explanation": "La IA generativa puede producir texto, imágenes, audio, código u otros contenidos."},
    {"id": 5, "category": "LLM", "difficulty": "Fácil", "question": "Qué significa LLM?", "options": ["Large Language Model", "Local Logic Memory", "Low Level Machine", "Linear Latency Map"], "answer": 0, "explanation": "LLM es un modelo grande de lenguaje entrenado para procesar y generar texto."},
    {"id": 6, "category": "Prompts", "difficulty": "Fácil", "question": "Qué es un prompt?", "options": ["La instrucción que se da al modelo", "Un servidor web", "Una clave privada", "Un monitor de red"], "answer": 0, "explanation": "El prompt es la entrada que guía al modelo sobre que debe responder o hacer."},
    {"id": 7, "category": "Prompts", "difficulty": "Media", "question": "Qué mejora un buen prompt?", "options": ["Claridad, contexto y restricciones", "Más ruido en los datos", "Menos información", "Respuestas al azar"], "answer": 0, "explanation": "Un prompt claro reduce ambiguedad y ayuda al modelo a seguir el objetivo."},
    {"id": 8, "category": "Tokens", "difficulty": "Fácil", "question": "Qué es un token en un modelo de lenguaje?", "options": ["Una unidad de texto procesada", "Un puerto TCP", "Un archivo ZIP", "Una tarjeta gráfica"], "answer": 0, "explanation": "Los modelos procesan texto como tokens, que pueden ser palabras, partes de palabras o símbolos."},
    {"id": 9, "category": "LLM", "difficulty": "Media", "question": "Qué indica la ventana de contexto?", "options": ["Cuántos tokens puede considerar el modelo", "Cuánta RAM tiene el navegador", "Cuántos usuarios hay", "Cuántos discos existen"], "answer": 0, "explanation": "La ventana de contexto limita la cantidad de información que el modelo puede usar a la vez."},
    {"id": 10, "category": "IA Generativa", "difficulty": "Media", "question": "Qué controla la temperatura?", "options": ["La aleatoriedad de la salida", "La velocidad del ventilador", "El ancho de banda", "El tamaño de pantalla"], "answer": 0, "explanation": "Temperaturas bajas hacen salidas mas deterministas; altas aumentan variedad."},
    {"id": 11, "category": "IA Generativa", "difficulty": "Media", "question": "Qué es top-p sampling?", "options": ["Muestreo desde tokens con probabilidad acumulada", "Una métrica de disco", "Una tecnica de backup", "Una política de red"], "answer": 0, "explanation": "Top-p limita la seleccion a tokens cuya probabilidad acumulada alcanza un umbral."},
    {"id": 12, "category": "RAG", "difficulty": "Fácil", "question": "Qué significa RAG?", "options": ["Retrieval Augmented Generation", "Random Access Gateway", "Reactive Audio Graph", "Rule Assigned Group"], "answer": 0, "explanation": "RAG combina recuperación de información con generación de respuestas."},
    {"id": 13, "category": "RAG", "difficulty": "Media", "question": "Para qué sirve RAG?", "options": ["Dar contexto externo al modelo", "Eliminar todos los datos", "Cambiar el color de la app", "Apagar el servidor"], "answer": 0, "explanation": "RAG ayuda a responder usando documentos o conocimiento actualizado."},
    {"id": 14, "category": "RAG", "difficulty": "Media", "question": "Qué es chunking?", "options": ["Dividir documentos en fragmentos", "Mezclar contraseñas", "Reiniciar modelos", "Cambiar idioma del navegador"], "answer": 0, "explanation": "Chunking divide documentos largos para recuperar fragmentos relevantes."},
    {"id": 15, "category": "Embeddings", "difficulty": "Fácil", "question": "Qué es un embedding?", "options": ["Una representación numérica de significado", "Una imagen decorativa", "Un servidor fisico", "Un archivo temporal"], "answer": 0, "explanation": "Un embedding convierte datos como texto en vectores comparables."},
    {"id": 16, "category": "Embeddings", "difficulty": "Media", "question": "Qué permite comparar embeddings?", "options": ["Similitud semántica", "Voltaje eléctrico", "Tamaño de monitor", "Número de carpetas"], "answer": 0, "explanation": "La distancia o similitud entre vectores aproxima relacion de significado."},
    {"id": 17, "category": "Embeddings", "difficulty": "Difícil", "question": "Que métrica es común para comparar vectores?", "options": ["Similitud coseno", "Tiempo de arranque", "Uso de teclado", "TTL de DNS"], "answer": 0, "explanation": "La similitud coseno compara dirección entre vectores."},
    {"id": 18, "category": "Busqueda Vectorial", "difficulty": "Media", "question": "Qué guarda una base vectorial?", "options": ["Vectores y metadatos", "Solo contraseñas", "Solo imágenes PNG", "Reglas CSS"], "answer": 0, "explanation": "Una base vectorial permite buscar elementos similares por representación numérica."},
    {"id": 19, "category": "RAG", "difficulty": "Difícil", "question": "Qué hace un reranker?", "options": ["Reordena resultados por relevancia", "Entrena una red electrica", "Cifra toda la app", "Borra preguntas"], "answer": 0, "explanation": "Un reranker mejora el orden de documentos recuperados antes de generar la respuesta."},
    {"id": 20, "category": "Evaluación", "difficulty": "Fácil", "question": "Qué mide accuracy?", "options": ["Proporción total de aciertos", "Costo por token", "Ancho de red", "Tamaño del prompt"], "answer": 0, "explanation": "Accuracy mide el porcentaje de predicciones correctas sobre el total."},
    {"id": 21, "category": "Evaluación", "difficulty": "Media", "question": "Qué mide precisión?", "options": ["Aciertos positivos sobre positivos predichos", "Bytes por segundo", "Cantidad de usuarios", "Tiempo de despliegue"], "answer": 0, "explanation": "Precision indica cuantos positivos predichos realmente eran positivos."},
    {"id": 22, "category": "Evaluación", "difficulty": "Media", "question": "Qué mide recall?", "options": ["Positivos encontrados sobre positivos reales", "Número de prompts", "Uso de pantalla", "Cantidad de colores"], "answer": 0, "explanation": "Recall indica cuantos casos positivos reales fueron detectados."},
    {"id": 23, "category": "Evaluación", "difficulty": "Difícil", "question": "Qué resume F1-score?", "options": ["Balance entre precisión y recall", "Tamaño de batch solamente", "Costo de almacenamiento", "Uso de red"], "answer": 0, "explanation": "F1 es la media armónica de precisión y recall."},
    {"id": 24, "category": "Entrenamiento", "difficulty": "Fácil", "question": "Qué es aprendizaje supervisado?", "options": ["Entrenar con datos etiquetados", "Aprender sin ejemplos", "Responder sin entrada", "Guardar logs"], "answer": 0, "explanation": "El aprendizaje supervisado usa ejemplos con respuesta esperada."},
    {"id": 25, "category": "Entrenamiento", "difficulty": "Media", "question": "Qué es aprendizaje no supervisado?", "options": ["Descubrir patrones sin etiquetas", "Copiar respuestas humanas", "Usar solo imágenes", "Ignorar datos"], "answer": 0, "explanation": "El modelo busca estructura en datos sin etiquetas explicitas."},
    {"id": 26, "category": "Entrenamiento", "difficulty": "Media", "question": "Qué es reinforcement learning?", "options": ["Aprender por recompensas y acciones", "Traducir texto solamente", "Guardar imágenes", "Enviar correos"], "answer": 0, "explanation": "Un agente aprende tomando acciones y recibiendo recompensas o penalizaciones."},
    {"id": 27, "category": "Entrenamiento", "difficulty": "Media", "question": "Qué es overfitting?", "options": ["Memorizar entrenamiento y generalizar mal", "Aprender demasiado lento siempre", "Tener pocos archivos", "Reducir resolución"], "answer": 0, "explanation": "Overfitting ocurre cuando el modelo se ajusta demasiado a datos de entrenamiento."},
    {"id": 28, "category": "Entrenamiento", "difficulty": "Media", "question": "Qué ayuda a detectar overfitting?", "options": ["Comparar train y validación", "Cambiar fondo de pantalla", "Aumentar permisos", "Usar nombres largos"], "answer": 0, "explanation": "Si el modelo va bien en entrenamiento y mal en validación, puede haber overfitting."},
    {"id": 29, "category": "Datos", "difficulty": "Fácil", "question": "Por qué importa la calidad de datos?", "options": ["Porque afecta el aprendizaje del modelo", "Porque cambia el logo", "Porque reduce el teclado", "Porque apaga la nube"], "answer": 0, "explanation": "Datos incompletos, sesgados o ruidosos afectan resultados del modelo."},
    {"id": 30, "category": "Datos", "difficulty": "Media", "question": "Qué es data leakage?", "options": ["Filtrar información del futuro al entrenamiento", "Perder conexión Wi-Fi", "Duplicar botones", "Eliminar estilos"], "answer": 0, "explanation": "Data leakage infla métricas al incluir información que no estaría disponible en producción."},
    {"id": 31, "category": "Ética", "difficulty": "Fácil", "question": "Qué es sesgo en IA?", "options": ["Resultados injustos por datos o diseño", "Una mejora de velocidad", "Un tipo de servidor", "Un formato de imagen"], "answer": 0, "explanation": "El sesgo puede causar resultados desiguales entre grupos o contextos."},
    {"id": 32, "category": "Ética", "difficulty": "Media", "question": "Qué práctica protege datos personales?", "options": ["Minimizar y anonimizar datos", "Publicar todo el dataset", "Compartir claves", "Quitar auditoría"], "answer": 0, "explanation": "Minimizar, anonimizar y controlar acceso reduce riesgos de privacidad."},
    {"id": 33, "category": "Ética", "difficulty": "Media", "question": "Qué es explicabilidad?", "options": ["Capacidad de entender una decisión del modelo", "Convertir audio a video", "Comprimir archivos", "Cambiar una IP"], "answer": 0, "explanation": "La explicabilidad ayuda a entender por qué un modelo produjo una salida."},
    {"id": 34, "category": "Seguridad IA", "difficulty": "Media", "question": "Qué es una alucinacion?", "options": ["Una respuesta falsa pero convincente", "Una mejora de memoria", "Una tabla pequeña", "Una red privada"], "answer": 0, "explanation": "Los modelos pueden generar contenido incorrecto con apariencia de certeza."},
    {"id": 35, "category": "Seguridad IA", "difficulty": "Difícil", "question": "Qué es prompt injection?", "options": ["Intento de manipular instrucciones del modelo", "Aumentar batch size", "Convertir texto a minusculas", "Ordenar una lista"], "answer": 0, "explanation": "Prompt injection intenta alterar reglas, revelar datos o forzar acciones no deseadas."},
    {"id": 36, "category": "Seguridad IA", "difficulty": "Difícil", "question": "Qué mitiga prompt injection en RAG?", "options": ["Separar instrucciones y validar fuentes", "Confiar en cualquier texto", "Desactivar controles", "Ignorar logs"], "answer": 0, "explanation": "Separar contenido no confiable de instrucciones del sistema reduce ataques."},
    {"id": 37, "category": "NLP", "difficulty": "Fácil", "question": "Qué es NLP?", "options": ["Procesamiento de lenguaje natural", "Nuevo protocolo local", "Nodo de baja potencia", "Número logico primario"], "answer": 0, "explanation": "NLP trata tareas de lenguaje como clasificación, traduccion, resumen y dialogo."},
    {"id": 38, "category": "NLP", "difficulty": "Media", "question": "Qué tarea resume texto largo?", "options": ["Summarization", "Regression", "Clustering", "Rendering"], "answer": 0, "explanation": "Summarization reduce un texto manteniendo ideas principales."},
    {"id": 39, "category": "NLP", "difficulty": "Media", "question": "Qué hace sentiment analysis?", "options": ["Detecta polaridad u opinión", "Calcula voltaje", "Genera claves SSH", "Dibuja mapas"], "answer": 0, "explanation": "Analiza si un texto expresa sentimiento positivo, negativo o neutral."},
    {"id": 40, "category": "Visión", "difficulty": "Fácil", "question": "Qué es computer vision?", "options": ["IA para interpretar imágenes y video", "Un monitor curvo", "Un tipo de teclado", "Un cable HDMI"], "answer": 0, "explanation": "Computer vision permite detectar, clasificar o segmentar información visual."},
    {"id": 41, "category": "Visión", "difficulty": "Media", "question": "Qué es object detection?", "options": ["Localizar y clasificar objetos", "Traducir párrafos", "Ajustar temperatura", "Ordenar tokens"], "answer": 0, "explanation": "Object detection identifica objetos y su posición en una imagen."},
    {"id": 42, "category": "Visión", "difficulty": "Media", "question": "Qué es segmentacion semántica?", "options": ["Clasificar píxeles por categoría", "Comprimir video", "Crear prompts", "Medir recall"], "answer": 0, "explanation": "La segmentacion asigna una clase a cada pixel o región de una imagen."},
    {"id": 43, "category": "Audio", "difficulty": "Fácil", "question": "Qué hace speech-to-text?", "options": ["Convierte voz en texto", "Convierte imagen en red", "Cifra prompts", "Entrena sin datos"], "answer": 0, "explanation": "Speech-to-text transcribe audio hablado a texto."},
    {"id": 44, "category": "Audio", "difficulty": "Media", "question": "Qué hace text-to-speech?", "options": ["Convierte texto en voz", "Calcula F1", "Ordena vectores", "Detecta sesgo"], "answer": 0, "explanation": "Text-to-speech genera audio hablado desde texto."},
    {"id": 45, "category": "Modelos", "difficulty": "Media", "question": "Qué es fine-tuning?", "options": ["Ajustar un modelo con datos específicos", "Borrar el dataset", "Aumentar brillo", "Cambiar DNS"], "answer": 0, "explanation": "Fine-tuning adapta un modelo base a una tarea o dominio particular."},
    {"id": 46, "category": "Modelos", "difficulty": "Difícil", "question": "Qué es distillation?", "options": ["Entrenar un modelo pequeño usando uno grande", "Eliminar metadatos", "Crear una clave", "Ordenar imágenes"], "answer": 0, "explanation": "La destilacion transfiere conocimiento de un modelo grande a otro más eficiente."},
    {"id": 47, "category": "Modelos", "difficulty": "Media", "question": "Qué es inferencia?", "options": ["Usar un modelo para producir una salida", "Reentrenar todos los datos", "Cambiar un puerto", "Crear un archivo CSS"], "answer": 0, "explanation": "Inferencia es ejecutar el modelo ya entrenado para obtener predicciones o respuestas."},
    {"id": 48, "category": "MLOps", "difficulty": "Media", "question": "Qué es drift de datos?", "options": ["Cambio en distribucion de datos con el tiempo", "Duplicacion de botones", "Error de ortografia", "Borrado de logs"], "answer": 0, "explanation": "El drift puede degradar el rendimiento si los datos reales cambian."},
    {"id": 49, "category": "MLOps", "difficulty": "Media", "question": "Qué conviene monitorear en producción?", "options": ["Calidad, latencia, costo y errores", "Solo el color", "Solo el titulo", "Nada despues de lanzar"], "answer": 0, "explanation": "Monitorear modelos permite detectar degradacion, costos altos y fallos."},
    {"id": 50, "category": "MLOps", "difficulty": "Difícil", "question": "Qué es canary release para modelos?", "options": ["Liberar a pocos usuarios antes de escalar", "Eliminar validación", "Entrenar sin datos", "Publicar claves"], "answer": 0, "explanation": "Canary reduce riesgo probando una version nueva con tráfico limitado."},
    {"id": 51, "category": "Arquitectura IA", "difficulty": "Media", "question": "Qué es un agente de IA?", "options": ["Sistema que decide acciones para lograr objetivos", "Un archivo de imagen", "Un tipo de cable", "Una tabla estática"], "answer": 0, "explanation": "Un agente puede planear, usar herramientas y ejecutar pasos hacia un objetivo."},
    {"id": 52, "category": "Arquitectura IA", "difficulty": "Difícil", "question": "Qué riesgo tienen agentes con herramientas?", "options": ["Ejecutar acciones no deseadas", "No poder leer texto", "No usar memoria", "Tener pocos colores"], "answer": 0, "explanation": "Los agentes necesitan permisos, validaciónes y límites para evitar acciones peligrosas."},
    {"id": 53, "category": "Prompts", "difficulty": "Media", "question": "Qué es few-shot prompting?", "options": ["Dar ejemplos en el prompt", "Entrenar por meses", "Eliminar contexto", "Cambiar tipografía"], "answer": 0, "explanation": "Few-shot incluye ejemplos para guíar formato y razonamiento del modelo."},
    {"id": 54, "category": "Prompts", "difficulty": "Media", "question": "Qué es zero-shot prompting?", "options": ["Pedir una tarea sin ejemplos", "Usar cero datos siempre", "Apagar el modelo", "Responder con imagen"], "answer": 0, "explanation": "Zero-shot pide al modelo resolver una tarea sin ejemplos específicos."},
    {"id": 55, "category": "Razonamiento", "difficulty": "Difícil", "question": "Qué mejora pedir pasos intermedios cuando aplica?", "options": ["Razonamiento y verificabilidad", "Consumo eléctrico", "Resolucion de pantalla", "Conexión Wi-Fi"], "answer": 0, "explanation": "Descomponer problemas puede mejorar exactitud en tareas complejas."},
    {"id": 56, "category": "Seguridad IA", "difficulty": "Media", "question": "Qué es red teaming de IA?", "options": ["Probar el sistema con ataques simulados", "Pintar la interfaz roja", "Crear backups", "Reducir memoria"], "answer": 0, "explanation": "Red teaming busca fallas, abusos y vulnerabilidades antes de producción."},
    {"id": 57, "category": "Evaluación LLM", "difficulty": "Difícil", "question": "Qué evalúa groundedness?", "options": ["Si la respuesta está apoyada en fuentes", "Si hay muchas imágenes", "Si el boton es rojo", "Si hay mas RAM"], "answer": 0, "explanation": "Groundedness mide si la respuesta se basa en el contexto proporcionado."},
    {"id": 58, "category": "Evaluación LLM", "difficulty": "Difícil", "question": "Qué evalúa toxicidad?", "options": ["Contenido ofensivo o danino", "Uso de CPU", "Número de tokens solamente", "Tamaño del dataset"], "answer": 0, "explanation": "La toxicidad mide riesgo de lenguaje ofensivo, abusivo o perjudicial."},
    {"id": 59, "category": "Costos IA", "difficulty": "Media", "question": "Qué puede reducir costo en llamadas a LLM?", "options": ["Limitar tokens y cachear respuestas", "Duplicar prompts", "Quitar límites", "Repetir requests"], "answer": 0, "explanation": "Controlar tokens, cache y volumen de llamadas ayuda a manejar costos."},
    {"id": 60, "category": "Producción IA", "difficulty": "Media", "question": "Qué conviene registrar en una app de IA?", "options": ["Versión, entrada, salida y métricas", "Contraseñas en claro", "Solo colores", "Nada por privacidad"], "answer": 0, "explanation": "La trazabilidad permite auditar calidad, errores y comportamiento del sistema."},
    {"id": 61, "category": "Arquitectura IA", "difficulty": "Difícil", "question": "Qué ventaja tiene usar evaluaciones automaticas antes de públicar un modelo?", "options": ["Detectar regresiones de calidad", "Evitar todo monitoreo", "Eliminar datos de validación", "Aumentar al azar la temperatura"], "answer": 0, "explanation": "Las evaluaciones automaticas comparan versiones y ayudan a detectar degradacion antes de producción."},
    {"id": 62, "category": "RAG", "difficulty": "Difícil", "question": "Qué problema aparece si los chunks son demasiado grandes?", "options": ["Menor precisión en recuperación", "Más privacidad por defecto", "Cero uso de tokens", "Mejor grounding siempre"], "answer": 0, "explanation": "Chunks muy grandes pueden traer ruido y ocupar contexto con información poco relevante."},
    {"id": 63, "category": "RAG", "difficulty": "Difícil", "question": "Qué indica baja precisión en recuperación?", "options": ["Muchos documentos irrelevantes", "Pocas respuestas creativas", "Demasiada compresion CSS", "Modelo sin interfaz"], "answer": 0, "explanation": "Si se recuperan muchos documentos irrelevantes, el generador recibe contexto débil o confuso."},
    {"id": 64, "category": "LLM", "difficulty": "Difícil", "question": "Qué riesgo aumenta cuando se sube mucho la temperatura?", "options": ["Respuestas menos consistentes", "Menos creatividad", "Más determinismo", "Cero variacion"], "answer": 0, "explanation": "Temperaturas altas aumentan variedad, pero también pueden reducir consistencia y exactitud."},
    {"id": 65, "category": "Evaluación LLM", "difficulty": "Difícil", "question": "Qué mide faithfulness en respuestas generadas?", "options": ["Si la respuesta respeta el contexto dado", "Si usa muchas palabras", "Si responde rápido", "Si tiene formato JSON"], "answer": 0, "explanation": "Faithfulness evalua si la respuesta se mantiene fiel a las evidencias o contexto."},
    {"id": 66, "category": "Seguridad IA", "difficulty": "Difícil", "question": "Qué es exfiltracion de datos en una app de IA?", "options": ["Sacar información sensible mediante respuestas", "Reducir el número de preguntas", "Cambiar el color principal", "Acelerar el render"], "answer": 0, "explanation": "Una app vulnerable puede revelar secretos, datos personales o instrucciones internas."},
    {"id": 67, "category": "Agentes IA", "difficulty": "Difícil", "question": "Qué control es clave cuando un agente puede usar herramientas?", "options": ["Permisos mínimos y aprobaciónes", "Acceso total sin límites", "Sin auditoría", "Prompts ocultos al equipo"], "answer": 0, "explanation": "Los agentes con herramientas deben tener límites, autorizaciones y trazabilidad."},
    {"id": 68, "category": "Modelos", "difficulty": "Difícil", "question": "Qué suele buscar la cuantización de modelos?", "options": ["Reducir memoria y costo de inferencia", "Aumentar siempre el dataset", "Eliminar métricas", "Hacer prompts mas largos"], "answer": 0, "explanation": "La cuantización reduce precisión numérica para ejecutar modelos con menos recursos."},
    {"id": 69, "category": "MLOps", "difficulty": "Difícil", "question": "Qué diferencia hay entre monitorear datos y monitorear modelo?", "options": ["Datos mira entradas; modelo mira desempeño", "Son exactamente iguales", "Modelo solo mira colores", "Datos solo mira botones"], "answer": 0, "explanation": "El monitoreo de datos observa distribuciones de entrada; el del modelo observa métricas y resultados."},
    {"id": 70, "category": "Responsible AI", "difficulty": "Difícil", "question": "Qué es human-in-the-loop?", "options": ["Intervención humana en decisiónes o revisión", "Un modelo sin usuarios", "Un prompt vacío", "Una red sin salida"], "answer": 0, "explanation": "Human-in-the-loop incorpora revisión o aprobación humana en pasos sensibles."}
]

PDF_QUESTIONS = [
    {"id": 101, "category": "OCI GenAI Professional", "difficulty": "Media", "question": "En decodificación de LLM, ¿qué efecto tiene la temperatura?", "options": ["Ajusta qué tan distribuida es la probabilidad de la siguiente palabra", "Reduce el tamaño del modelo", "Cambia el idioma del entrenamiento", "Elimina la necesidad de prompts"], "answer": 0, "explanation": "Una temperatura más alta aplana la distribución y permite salidas más variadas; una baja vuelve la salida más determinista."},
    {"id": 102, "category": "OCI GenAI Professional", "difficulty": "Media", "question": "¿Qué describe mejor el aprendizaje en contexto?", "options": ["Condicionar el modelo con instrucciones o ejemplos dentro del prompt", "Entrenar todos los pesos desde cero", "Crear una base vectorial", "Reducir el número de tokens del vocabulario"], "answer": 0, "explanation": "El aprendizaje en contexto guía al modelo usando instrucciones, ejemplos o demostraciones sin modificar sus pesos."},
    {"id": 103, "category": "OCI GenAI Professional", "difficulty": "Difícil", "question": "¿Cuándo es útil soft prompting frente a fine-tuning completo?", "options": ["Cuando se busca adaptar un modelo sin modificar todos sus pesos", "Cuando no existe un modelo base", "Cuando se quiere borrar el contexto", "Cuando solo se trabaja con imágenes"], "answer": 0, "explanation": "Soft prompting adapta el comportamiento del modelo con parámetros o prompts entrenables, reduciendo el costo frente a ajustar todo el modelo."},
    {"id": 104, "category": "Prompt Engineering", "difficulty": "Media", "question": "¿Qué busca la ingeniería de prompts?", "options": ["Diseñar instrucciones que guíen mejor la respuesta del modelo", "Cambiar el hardware del servidor", "Eliminar la evaluación del modelo", "Reemplazar el dataset por completo"], "answer": 0, "explanation": "La ingeniería de prompts estructura instrucciones, contexto, ejemplos y restricciones para obtener respuestas más útiles."},
    {"id": 105, "category": "LLM", "difficulty": "Media", "question": "En LLM, ¿qué significa una alucinación?", "options": ["Una respuesta incorrecta presentada con confianza", "Una técnica de compresión", "Un índice vectorial", "Un tipo de token especial"], "answer": 0, "explanation": "Una alucinación ocurre cuando el modelo genera información falsa o no respaldada."},
    {"id": 106, "category": "OCI GenAI Service", "difficulty": "Media", "question": "¿Por qué se usan GPUs en clústeres dedicados para IA generativa?", "options": ["Porque aceleran cálculos paralelos intensivos", "Porque reemplazan los prompts", "Porque almacenan documentos", "Porque evitan usar embeddings"], "answer": 0, "explanation": "Las GPUs aceleran operaciones matriciales y paralelas típicas del entrenamiento, ajuste e inferencia de modelos."},
    {"id": 107, "category": "Embeddings", "difficulty": "Media", "question": "¿Cuál es el propósito de los embeddings en NLP?", "options": ["Representar texto como vectores comparables", "Aumentar la longitud del prompt", "Guardar contraseñas", "Convertir audio en imágenes"], "answer": 0, "explanation": "Los embeddings capturan relaciones semánticas en un espacio vectorial."},
    {"id": 108, "category": "Generación", "difficulty": "Media", "question": "¿Qué puede pasar si se usa un punto como secuencia de parada?", "options": ["La generación puede detenerse al encontrar el primer punto", "El modelo genera respuestas infinitas", "Se entrena automáticamente", "Se elimina la temperatura"], "answer": 0, "explanation": "Una stop sequence detiene la salida cuando aparece; un punto puede cortar respuestas demasiado pronto."},
    {"id": 109, "category": "Prompts", "difficulty": "Media", "question": "¿Cuál es una ventaja de few-shot prompting?", "options": ["Personaliza la respuesta con pocos ejemplos en el prompt", "Actualiza todos los pesos del modelo", "Reduce a cero el uso de tokens", "Elimina la necesidad de evaluación"], "answer": 0, "explanation": "Few-shot prompting muestra ejemplos para que el modelo imite formato, tono o razonamiento esperado."},
    {"id": 110, "category": "Generación", "difficulty": "Difícil", "question": "¿Qué hace una penalización de frecuencia?", "options": ["Reduce la repetición de tokens ya usados", "Aumenta siempre la creatividad", "Selecciona solo la palabra más probable", "Convierte texto en vectores"], "answer": 0, "explanation": "Las penalizaciones de frecuencia disminuyen la probabilidad de repetir tokens que ya aparecieron."},
    {"id": 111, "category": "Búsqueda Semántica", "difficulty": "Media", "question": "¿Qué diferencia a la búsqueda semántica de la búsqueda por palabras clave?", "options": ["Busca por significado y similitud, no solo por coincidencias exactas", "Solo ordena alfabéticamente", "No usa datos", "Solo funciona con números"], "answer": 0, "explanation": "La búsqueda semántica usa embeddings para encontrar contenido relacionado aunque no comparta las mismas palabras."},
    {"id": 112, "category": "RAG", "difficulty": "Media", "question": "En un sistema RAG, ¿qué hace el generador?", "options": ["Produce texto usando la consulta y la información recuperada", "Guarda todos los documentos", "Asigna direcciones IP", "Elimina el ranking"], "answer": 0, "explanation": "El generador usa el contexto recuperado y la pregunta original para crear una respuesta coherente."},
    {"id": 113, "category": "RAG", "difficulty": "Media", "question": "¿Qué limitación tiene un LLM sin RAG?", "options": ["No puede consultar conocimiento externo actualizado durante la respuesta", "No puede generar texto", "No puede usar tokens", "No puede recibir prompts"], "answer": 0, "explanation": "Sin RAG, el modelo depende principalmente de su entrenamiento y del contexto incluido en el prompt."},
    {"id": 114, "category": "RAG", "difficulty": "Media", "question": "¿Qué hace el ranker en una aplicación de generación con recuperación?", "options": ["Ordena la información recuperada por relevancia", "Entrena el modelo base", "Cifra el prompt", "Crea la interfaz web"], "answer": 0, "explanation": "El ranker prioriza los fragmentos más relevantes antes de enviarlos al generador."},
    {"id": 115, "category": "LangChain", "difficulty": "Media", "question": "¿Para qué sirve la memoria en LangChain?", "options": ["Mantener contexto histórico útil durante la conversación", "Reemplazar todos los prompts", "Guardar imágenes del navegador", "Evitar usar modelos"], "answer": 0, "explanation": "La memoria permite conservar datos de interacción para mejorar continuidad y decisiones en cadenas conversacionales."},
    {"id": 116, "category": "LangChain", "difficulty": "Media", "question": "En un chatbot, ¿qué función cumplen los prompts?", "options": ["Definen instrucciones, formato y contexto para el modelo", "Ejecutan consultas de red", "Sustituyen la base de datos", "Reducen el hardware necesario"], "answer": 0, "explanation": "Los prompts guían el comportamiento del modelo y estructuran la tarea."},
    {"id": 117, "category": "LangChain", "difficulty": "Difícil", "question": "¿Qué describe LCEL en LangChain?", "options": ["Una forma declarativa de componer cadenas", "Un tipo de GPU", "Una métrica de toxicidad", "Un algoritmo de compresión"], "answer": 0, "explanation": "LCEL permite componer pasos y componentes de una aplicación LLM de forma expresiva."},
    {"id": 118, "category": "Prompt Templates", "difficulty": "Media", "question": "¿Qué suelen usar los prompt templates para insertar variables?", "options": ["Sintaxis tipo str.format", "Consultas SQL únicamente", "Claves SSH", "Archivos binarios"], "answer": 0, "explanation": "Los templates permiten definir texto reutilizable con espacios para variables como pregunta, contexto o historial."},
    {"id": 119, "category": "Vector DB", "difficulty": "Difícil", "question": "¿Qué relación preserva una base vectorial para ayudar a un LLM?", "options": ["Relaciones semánticas entre conceptos", "Relaciones jerárquicas de carpetas", "Relaciones de puertos TCP", "Relaciones de estilos CSS"], "answer": 0, "explanation": "Las bases vectoriales permiten recuperar contenido semánticamente cercano, clave para contexto y precisión."},
    {"id": 120, "category": "RAG", "difficulty": "Media", "question": "¿Cuál es el objetivo principal de RAG en generación de texto?", "options": ["Generar usando información adicional recuperada de fuentes externas", "Generar sin contexto", "Desactivar el LLM", "Ordenar datos por fecha"], "answer": 0, "explanation": "RAG mejora respuestas al recuperar conocimiento externo relevante antes de generar."},
    {"id": 121, "category": "LangChain", "difficulty": "Media", "question": "¿Qué componente suele generar la salida lingüística en un chatbot con LangChain?", "options": ["El LLM", "El loader de documentos", "La hoja de estilos", "El balanceador"], "answer": 0, "explanation": "El LLM es responsable de producir la respuesta de lenguaje natural."},
    {"id": 122, "category": "Fine-tuning", "difficulty": "Difícil", "question": "¿Qué diferencia a fine-tuning completo de PEFT?", "options": ["Fine-tuning completo ajusta más pesos; PEFT ajusta una fracción", "PEFT siempre entrena desde cero", "Ambos no modifican nada", "Fine-tuning solo sirve para imágenes"], "answer": 0, "explanation": "PEFT busca adaptar modelos actualizando menos parámetros para reducir costo y riesgo de overfitting."},
    {"id": 123, "category": "Soft Prompting", "difficulty": "Difícil", "question": "¿En qué escenario encaja soft prompting?", "options": ["Guiar un LLM preentrenado sin entrenamiento específico completo", "Crear una red privada", "Eliminar embeddings", "Forzar respuestas sin prompt"], "answer": 0, "explanation": "Soft prompting permite adaptar modelos preentrenados con menor intervención que el ajuste completo."},
    {"id": 124, "category": "Evaluación", "difficulty": "Media", "question": "En entrenamiento, ¿qué representa la pérdida o loss?", "options": ["Qué tan equivocadas están las predicciones", "La cantidad de usuarios", "El número de GPUs", "La velocidad de red"], "answer": 0, "explanation": "La loss cuantifica el error del modelo y guía el proceso de optimización."},
    {"id": 125, "category": "Embeddings", "difficulty": "Media", "question": "Si dos embeddings tienen alta similitud coseno, ¿qué implica?", "options": ["Apuntan en direcciones similares", "Tienen textos idénticos siempre", "No tienen relación", "Son más pequeños"], "answer": 0, "explanation": "La similitud coseno mide orientación relativa; alta similitud sugiere relación semántica."},
    {"id": 126, "category": "RAG", "difficulty": "Difícil", "question": "¿Qué distingue recuperación y ranking en RAG?", "options": ["Recuperación encuentra candidatos; ranking prioriza relevancia", "Son el mismo paso exacto", "Ranking entrena el LLM", "Recuperación genera la respuesta final"], "answer": 0, "explanation": "Primero se buscan documentos candidatos y luego se ordenan para enviar los mejores al generador."},
    {"id": 127, "category": "Vector DB", "difficulty": "Media", "question": "¿Cómo se caracteriza una base de datos vectorial?", "options": ["Trabaja con distancias y similitudes en espacios vectoriales", "Solo almacena filas y columnas tradicionales", "No permite búsquedas", "Solo contiene contraseñas"], "answer": 0, "explanation": "Las bases vectoriales están optimizadas para encontrar vecinos cercanos en dimensiones altas."},
    {"id": 128, "category": "Fine-tuning", "difficulty": "Media", "question": "¿Cuándo conviene considerar fine-tuning?", "options": ["Cuando el modelo no cumple una tarea y el prompt no basta", "Cuando no hay datos", "Cuando se quiere evitar evaluación", "Cuando solo se necesita cambiar colores"], "answer": 0, "explanation": "Fine-tuning puede adaptar el modelo cuando el comportamiento requerido no se logra solo con prompting."},
    {"id": 129, "category": "Decodificación", "difficulty": "Media", "question": "¿Qué hace greedy decoding?", "options": ["Elige en cada paso el token más probable", "Elige siempre el token más raro", "Entrena embeddings", "Ordena documentos"], "answer": 0, "explanation": "Greedy decoding selecciona localmente la opción de mayor probabilidad en cada paso."},
    {"id": 130, "category": "Fine-tuning", "difficulty": "Difícil", "question": "¿Qué caracteriza a T-Few fine-tuning?", "options": ["Actualiza selectivamente una fracción de pesos", "Entrena todo desde cero", "Elimina el prompt", "No modifica ningún parámetro"], "answer": 0, "explanation": "T-Few busca reducir carga computacional y riesgo de overfitting ajustando pocos parámetros."}
]

VECTOR_SEARCH_QUESTIONS = [
    {"id": 201, "category": "OCI AI Vector Search", "difficulty": "Media", "question": "¿Qué problema principal resuelve Oracle AI Vector Search?", "options": ["Buscar por significado semántico en lugar de solo palabras clave", "Crear usuarios IAM automáticamente", "Reemplazar todas las consultas SQL", "Convertir una VCN en pública"], "answer": 0, "explanation": "AI Vector Search permite comparar embeddings para encontrar contenido semánticamente similar."},
    {"id": 202, "category": "Vector Search", "difficulty": "Fácil", "question": "¿Qué representa normalmente un embedding vectorial?", "options": ["El significado de un dato como números comparables", "Una contraseña cifrada", "Un puerto de red", "Un backup incremental"], "answer": 0, "explanation": "Un embedding transforma texto, imagen u otro contenido en un vector que conserva relaciones semánticas."},
    {"id": 203, "category": "Oracle Database", "difficulty": "Media", "question": "¿Qué tipo de dato permite guardar embeddings dentro de Oracle Database?", "options": ["VECTOR", "JSON_TABLE", "VARCHAR_SECRET", "IP_ADDRESS"], "answer": 0, "explanation": "El tipo VECTOR permite almacenar embeddings junto con datos relacionales en la base."},
    {"id": 204, "category": "Similarity Search", "difficulty": "Media", "question": "¿Qué mide una consulta de similitud vectorial?", "options": ["La cercanía entre vectores en un espacio matemático", "La cantidad de usuarios conectados", "La latencia de una subnet", "El tamaño de una clave SSH"], "answer": 0, "explanation": "La similitud se calcula con funciones de distancia entre vectores."},
    {"id": 205, "category": "Distance Metrics", "difficulty": "Media", "question": "¿Qué métrica se usa con frecuencia para comparar embeddings de texto?", "options": ["Cosine similarity", "MTU", "TTL", "CIDR overlap"], "answer": 0, "explanation": "La similitud coseno compara la orientación de los vectores y es común en búsqueda semántica."},
    {"id": 206, "category": "Vector Indexes", "difficulty": "Difícil", "question": "¿Cuál es el objetivo de un índice vectorial aproximado?", "options": ["Mejorar velocidad aceptando una compensación controlada de exactitud", "Eliminar la necesidad de embeddings", "Garantizar siempre cero latencia", "Convertir texto en audio"], "answer": 0, "explanation": "Los índices aproximados aceleran la búsqueda de vecinos cercanos a cambio de una precisión configurable."},
    {"id": 207, "category": "HNSW", "difficulty": "Difícil", "question": "¿Qué describe mejor un índice HNSW?", "options": ["Un grafo jerárquico en memoria para búsqueda aproximada", "Un índice exclusivo para claves primarias", "Una tabla temporal global", "Un algoritmo para comprimir imágenes"], "answer": 0, "explanation": "HNSW usa una estructura de grafo para navegar rápidamente hacia vectores cercanos."},
    {"id": 208, "category": "IVF", "difficulty": "Difícil", "question": "¿Qué describe mejor un índice IVF?", "options": ["Un índice basado en particiones o listas invertidas", "Un índice de texto para expresiones regulares", "Un mecanismo de autenticación OCI", "Un modelo generativo de imágenes"], "answer": 0, "explanation": "IVF organiza vectores en particiones para reducir el espacio de búsqueda."},
    {"id": 209, "category": "Vector Indexes", "difficulty": "Media", "question": "En Oracle AI Vector Search, ¿qué tipos de índices vectoriales se usan comúnmente para búsqueda aproximada?", "options": ["HNSW e IVF", "B-tree y bitmap únicamente", "DNS y WAF", "NAT y DRG"], "answer": 0, "explanation": "HNSW e IVF son estructuras usadas para acelerar búsquedas vectoriales aproximadas."},
    {"id": 210, "category": "SQL Vector Search", "difficulty": "Difícil", "question": "¿Qué función SQL se usa típicamente para ordenar resultados por cercanía vectorial?", "options": ["VECTOR_DISTANCE", "DBMS_RANDOM", "TO_CHAR", "UTL_HTTP"], "answer": 0, "explanation": "VECTOR_DISTANCE calcula la distancia entre el vector almacenado y el vector de consulta."},
    {"id": 211, "category": "SQL Vector Search", "difficulty": "Difícil", "question": "¿Qué condición ayuda a que el optimizador considere un índice vectorial aproximado?", "options": ["Usar la palabra clave APPROX o APPROXIMATE en la búsqueda", "Eliminar el ORDER BY", "Convertir el vector a texto", "Usar solo SELECT *"], "answer": 0, "explanation": "Para búsquedas aproximadas, la consulta debe indicar que puede usar aproximación."},
    {"id": 212, "category": "Distance Metrics", "difficulty": "Difícil", "question": "¿Qué debe coincidir para que un índice vectorial sea usado correctamente por la consulta?", "options": ["La métrica de distancia del índice y la de VECTOR_DISTANCE", "El nombre del alias del jugador", "El tamaño del navegador", "La región de Object Storage"], "answer": 0, "explanation": "Si la métrica del índice no coincide con la función de distancia, el plan puede no usar el índice."},
    {"id": 213, "category": "Embeddings", "difficulty": "Media", "question": "¿Por qué todos los vectores de un índice deben tener dimensiones compatibles?", "options": ["Porque la distancia no se calcula bien entre vectores de longitudes distintas", "Porque SQL no permite números decimales", "Porque los índices solo aceptan texto", "Porque la red bloquea dimensiones impares"], "answer": 0, "explanation": "Las operaciones de distancia requieren vectores con la misma dimensionalidad."},
    {"id": 214, "category": "RAG con Oracle", "difficulty": "Media", "question": "En una arquitectura RAG, ¿para qué sirve AI Vector Search?", "options": ["Recuperar fragmentos relevantes antes de llamar al LLM", "Reemplazar el prompt del usuario", "Asignar IPs privadas", "Crear políticas IAM"], "answer": 0, "explanation": "La búsqueda vectorial encuentra contexto relacionado que el modelo puede usar para generar respuestas más fundamentadas."},
    {"id": 215, "category": "RAG con Oracle", "difficulty": "Difícil", "question": "¿Qué se almacena normalmente junto al vector de un documento?", "options": ["Texto, metadatos e identificadores del fragmento", "Solo reglas de firewall", "La contraseña de ADMIN", "El color de la interfaz"], "answer": 0, "explanation": "Guardar texto y metadatos permite mostrar fuentes, filtrar y construir contexto para el LLM."},
    {"id": 216, "category": "Chunking", "difficulty": "Difícil", "question": "¿Por qué el chunking es importante antes de crear embeddings de documentos largos?", "options": ["Mejora la recuperación de fragmentos precisos y relevantes", "Elimina la necesidad de una base de datos", "Garantiza respuestas siempre correctas", "Convierte SQL en HTML"], "answer": 0, "explanation": "Fragmentos bien definidos reducen ruido y mejoran la precisión de la recuperación."},
    {"id": 217, "category": "Hybrid Search", "difficulty": "Difícil", "question": "¿Qué busca una estrategia híbrida de búsqueda?", "options": ["Combinar señales semánticas y búsqueda tradicional", "Usar solo una tabla temporal", "Evitar todo ranking", "Consultar sin índices"], "answer": 0, "explanation": "La búsqueda híbrida puede combinar coincidencias por texto con similitud vectorial para mejorar resultados."},
    {"id": 218, "category": "ONNX", "difficulty": "Difícil", "question": "¿Qué ventaja ofrece importar un modelo compatible ONNX en Oracle Database?", "options": ["Generar embeddings dentro de la base con SQL", "Crear VCNs automáticamente", "Desactivar TLS", "Convertir índices en backups"], "answer": 0, "explanation": "Un modelo ONNX importado puede usarse para generar embeddings cerca de los datos."},
    {"id": 219, "category": "VECTOR_EMBEDDING", "difficulty": "Difícil", "question": "¿Qué devuelve la función VECTOR_EMBEDDING?", "options": ["Un valor de tipo VECTOR", "Una política IAM", "Un archivo ZIP", "Una dirección IP pública"], "answer": 0, "explanation": "VECTOR_EMBEDDING genera un embedding usando un modelo importado y devuelve un vector."},
    {"id": 220, "category": "Vector Search", "difficulty": "Media", "question": "¿Qué significa recuperar los k vecinos más cercanos?", "options": ["Traer los k vectores más similares a la consulta", "Crear k usuarios nuevos", "Abrir k puertos TCP", "Ejecutar k backups"], "answer": 0, "explanation": "La búsqueda de vecinos cercanos devuelve los resultados con menor distancia o mayor similitud."},
    {"id": 221, "category": "Calidad RAG", "difficulty": "Difícil", "question": "¿Qué puede indicar un top-k demasiado alto en RAG?", "options": ["Más ruido en el contexto enviado al modelo", "Menos uso de tokens siempre", "Cero riesgo de alucinación", "Imposibilidad de usar embeddings"], "answer": 0, "explanation": "Recuperar demasiados fragmentos puede llenar el contexto con información irrelevante."},
    {"id": 222, "category": "Calidad RAG", "difficulty": "Difícil", "question": "¿Qué puede indicar un top-k demasiado bajo en RAG?", "options": ["Pérdida de contexto relevante", "Más precisión garantizada", "Menor necesidad de evaluación", "Eliminación del ranking"], "answer": 0, "explanation": "Si se recuperan pocos fragmentos, puede faltar evidencia importante para responder."},
    {"id": 223, "category": "Seguridad IA", "difficulty": "Difícil", "question": "¿Qué riesgo debe controlarse al indexar documentos internos en una base vectorial?", "options": ["Exposición de información sensible por recuperación o respuesta", "Falta de colores en la UI", "Aumento de tamaño de fuente", "Uso de botones redondos"], "answer": 0, "explanation": "La seguridad debe filtrar documentos por permisos y evitar que el LLM revele datos no autorizados."},
    {"id": 224, "category": "Evaluación Vector Search", "difficulty": "Difícil", "question": "¿Qué métrica ayuda a evaluar si la recuperación trae documentos relevantes?", "options": ["Precision@k o recall@k", "OCPU por región", "Tiempo de DNS", "Número de subnets"], "answer": 0, "explanation": "Precision@k y recall@k miden calidad de los resultados recuperados frente a resultados esperados."},
    {"id": 225, "category": "Arquitectura OCI", "difficulty": "Media", "question": "¿Cuál es una ventaja de guardar vectores y datos de negocio en Oracle Database?", "options": ["Aplicar SQL, seguridad y transacciones sobre ambos", "Evitar cualquier modelo de embedding", "Eliminar todos los índices", "No necesitar backups"], "answer": 0, "explanation": "Mantener vectores junto a datos transaccionales permite gobernanza, consultas y seguridad integradas."}
]

QUESTIONS = QUESTIONS + PDF_QUESTIONS + VECTOR_SEARCH_QUESTIONS

ROUNDS = {}
QUESTION_COUNT = 10
SCORE_PER_QUESTION = 10

app = Flask(__name__)


def get_connection():
    if not DB_PASSWORD:
        raise RuntimeError("AIQUIZ_DB_PASSWORD is not configured")
    return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)


def init_db():
    ddl = """
    BEGIN
      EXECUTE IMMEDIATE '
        CREATE TABLE ai_quiz_scores (
          id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
          alias VARCHAR2(80) NOT NULL,
          score NUMBER NOT NULL,
          total_questions NUMBER NOT NULL,
          duration_seconds NUMBER,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        )';
    EXCEPTION
      WHEN OTHERS THEN
        IF SQLCODE != -955 THEN
          RAISE;
        END IF;
    END;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/questions")
def questions():
    harder = [q for q in QUESTIONS if q["difficulty"] in ("Media", "Difícil")]
    selected_harder = random.sample(harder, min(7, len(harder)))
    remaining = [q for q in QUESTIONS if q["id"] not in {item["id"] for item in selected_harder}]
    selected = selected_harder + random.sample(remaining, QUESTION_COUNT - len(selected_harder))
    random.shuffle(selected)
    round_id = uuid.uuid4().hex
    round_answers = {}
    payload = []
    for q in selected:
        options = list(enumerate(q["options"]))
        random.shuffle(options)
        shuffled = [value for _, value in options]
        correct_index = next(index for index, (original_index, _) in enumerate(options) if original_index == q["answer"])
        round_answers[q["id"]] = correct_index
        payload.append(
            {
                "id": q["id"],
                "category": q["category"],
                "difficulty": q["difficulty"],
                "question": q["question"],
                "options": shuffled,
            }
        )
    ROUNDS[round_id] = {"answers": round_answers, "created": int(time.time())}
    payload = [
        item for item in payload
    ]
    return jsonify({"roundId": round_id, "questions": payload, "startedAt": int(time.time())})


@app.post("/api/submit")
def submit():
    data = request.get_json(force=True)
    alias = "Participante"
    answers = data.get("answers", [])
    round_data = ROUNDS.get(str(data.get("roundId", "")), {"answers": {}})
    started_at = int(data.get("startedAt", int(time.time())))
    by_id = {q["id"]: q for q in QUESTIONS}

    results = []
    score = 0
    for item in answers:
        q = by_id.get(int(item.get("id", 0)))
        if not q:
            continue
        selected = int(item.get("selected", -1))
        correct_index = int(round_data["answers"].get(q["id"], q["answer"]))
        correct = selected == correct_index
        if correct:
            score += SCORE_PER_QUESTION
        results.append(
            {
                "id": q["id"],
                "correct": correct,
                "correctIndex": correct_index,
                "message": "Muy bien jugado amigo" if correct else "No pasa nada, sigue intentando",
                "explanation": q["explanation"],
            }
        )

    duration = max(0, int(time.time()) - started_at)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ai_quiz_scores(alias, score, total_questions, duration_seconds)
                VALUES (:alias, :score, :total_questions, :duration_seconds)
                """,
                alias=alias,
                score=score,
                total_questions=len(results),
                duration_seconds=duration,
            )
        conn.commit()

    return jsonify(
        {
            "score": score,
            "maxScore": len(results) * SCORE_PER_QUESTION,
            "durationSeconds": duration,
            "results": results,
        }
    )


@app.post("/api/check")
def check_answer():
    data = request.get_json(force=True)
    round_data = ROUNDS.get(str(data.get("roundId", "")), {"answers": {}})
    q = {item["id"]: item for item in QUESTIONS}.get(int(data.get("id", 0)))
    if not q:
        return jsonify({"error": "Question not found"}), 404
    selected = int(data.get("selected", -1))
    correct_index = int(round_data["answers"].get(q["id"], q["answer"]))
    correct = selected == correct_index
    return jsonify(
        {
            "id": q["id"],
            "correct": correct,
            "correctIndex": correct_index,
            "message": "Muy bien jugado amigo" if correct else "No pasa nada, sigue intentando",
            "explanation": q["explanation"],
        }
    )


@app.get("/api/leaderboard")
def leaderboard():
    return jsonify({"leaderboard": []})


@app.get("/health")
def health():
    return jsonify({"ok": True, "app": "ready", "database": "not_required"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
