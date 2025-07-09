"""
Modelos de datos usando Pydantic para validación de tipos.
Define la estructura de datos de entrada y salida de la API.
"""
from pydantic import BaseModel, Field
from typing import Optional

class MessageRequest(BaseModel):
    """
    Modelo para solicitud de envío de mensaje.
    Valida que el teléfono, mensaje e instancia sean correctos.
    """
    phone: str = Field(..., description="Número de teléfono en formato internacional", min_length=10)
    message: str = Field(..., description="Mensaje a enviar", min_length=1)
    instance_name: str = Field(default="default", description="Nombre de la instancia de Evolution API")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "phone": "+52123456789",
                "message": "Hola Carlos, este es un mensaje de prueba",
                "instance_name": "default"
            }
        }
    }

class MessageResponse(BaseModel):
    """
    Modelo para respuesta de la API.
    Indica el estado del procesamiento del mensaje.
    """
    success: bool = Field(..., description="Indica si la solicitud fue procesada correctamente")
    message: str = Field(..., description="Mensaje descriptivo del resultado")
    task_id: Optional[str] = Field(None, description="ID de la tarea Celery para seguimiento")
    
class TaskStatus(BaseModel):
    """
    Modelo para consultar el estado de una tarea.
    """
    task_id: str
    status: str
    result: Optional[dict] = None 