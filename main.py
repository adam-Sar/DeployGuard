from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal, List
load_dotenv()

model_name = os.getenv("MODEL")
api = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api
)

class ReportModel(BaseModel):
    """Alert report structure"""
    time: str = Field(description="Time in which the error occured")
    service: str = Field(description="The service/services affected by the error")
    cause: str = Field(description="The likely root cause of the error")
    evidence: str = Field(description="Evidence from the logs")
    next_step: str = Field(description="Recommended next steps")
    incident: bool = Field(description="The incident had already occured")
    alert: bool = Field(description="The incident hadn't yet occured, but expected due to the errors observed")
    fact: Literal["confirmed", "likely", "uncertain"] = Field(description="how sure are we about the root cause, the incident happening, and the services getting affected by the error")

class Reports(BaseModel):
    """Multiple report models in case of multiple errors or/and root causes"""
    reports: List[ReportModel]

structured_model = model.with_structured_output(Reports)
prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are an experienced Infrastructure Engineer specializing in
        infrastructure monitoring and incident investigation.

        Analyze infrastructure logs and identify incidents, failures,
        and potential risks.

        Base your conclusions strictly on the provided evidence.
        Do not assume a root cause when the logs do not prove one.
        Distinguish confirmed facts from likely explanations and uncertain hypotheses.

        For every identified issue:
        - Include the relevant timestamp and affected service.
        - Explain the likely cause using evidence from the logs.
        - Recommend practical next steps to investigate or resolve it.
        - Avoid recommending disruptive actions such as rollback unless
          the available evidence justifies them.

        Do not invent events, metrics, or causes that are not present in the logs.
    """),
    ("human", """
        Analyze the following infrastructure logs:

        {logs}

        Return a structured report for each identified issue.
    """)
])

chain = prompt | structured_model

result = chain.invoke({
    "logs": """
                {"timestamp":"2026-10-31T12:00:00Z","source":"ecs_service_event","service":"orders-api","message":"Deployment started using task definition orders-api:42."}
                {"timestamp":"2026-10-31T12:03:45Z","source":"ecs_service_event","service":"orders-api","task_id":"task-a17","message":"Task failed ALB health checks; target returned HTTP 503."}
                {"timestamp":"2026-10-31T12:04:14Z","source":"ecs_task_state_change","service":"orders-api","task_id":"task-b28","lastStatus":"STOPPED","stopCode":"EssentialContainerExited","stoppedReason":"Essential container in task exited","container":{"name":"orders-api","exitCode":137,"reason":"OutOfMemoryError: Container killed due to memory usage"}}
                {"timestamp":"2026-10-31T12:04:29Z","source":"ecs_service_event","service":"orders-api","message":"Replacement task task-d40 started."}
                {"timestamp":"2026-10-31T12:05:03Z","source":"ecs_service_event","service":"orders-api","task_id":"task-d40","message":"Task failed ALB health checks; target returned HTTP 503."}
            """
})

json_string = result.model_dump_json(indent=2)
print(json_string)