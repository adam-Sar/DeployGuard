from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

model_name = os.getenv("MODEL")
api = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "you are an expert Infrastructure Engineer with expertise in incident investigation"),
    ("human", "Based on the following logs:{logs}, what incident had happened or is expected to happen ")
])

chain = prompt | model | StrOutputParser()

result = chain.invoke({
    "logs": """
                {"timestamp":"2026-10-31T12:00:00Z","source":"ecs_service_event","service":"orders-api","message":"Deployment started using task definition orders-api:42."}
                {"timestamp":"2026-10-31T12:03:45Z","source":"ecs_service_event","service":"orders-api","task_id":"task-a17","message":"Task failed ALB health checks; target returned HTTP 503."}
                {"timestamp":"2026-10-31T12:04:14Z","source":"ecs_task_state_change","service":"orders-api","task_id":"task-b28","lastStatus":"STOPPED","stopCode":"EssentialContainerExited","stoppedReason":"Essential container in task exited","container":{"name":"orders-api","exitCode":137,"reason":"OutOfMemoryError: Container killed due to memory usage"}}
                {"timestamp":"2026-10-31T12:04:29Z","source":"ecs_service_event","service":"orders-api","message":"Replacement task task-d40 started."}
                {"timestamp":"2026-10-31T12:05:03Z","source":"ecs_service_event","service":"orders-api","task_id":"task-d40","message":"Task failed ALB health checks; target returned HTTP 503."}
            """
})

print(result)