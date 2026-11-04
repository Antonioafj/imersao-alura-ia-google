# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import Capabilities, GCSToolSettings
from google.adk.models import Gemini
from google.adk.skills import load_skills_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types


# Diretórios do projeto
APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
SKILLS_DIR = APP_DIR / "skills"
PLANOS_DIR = PROJECT_DIR / "planos"
PLANOS_DIR.mkdir(parents=True, exist_ok=True)

# Carrega variáveis de ambiente
load_dotenv(PROJECT_DIR / ".env")

# Configuração do bucket GCS e GCSToolset
GCS_BUCKET_NAME = os.getenv(
    "GCS_BUCKET_NAME", "agente-estudos-planos-molten-box-513201-m7"
)
gcs_toolset = GCSToolset(
    tool_filter=["create_object", "get_object_data", "list_objects"],
    gcs_tool_settings=GCSToolSettings(
        capabilities=[Capabilities.READ_WRITE],
        local_file_root=str(PLANOS_DIR),
    ),
)

# Carregamento das ADK Skills com SkillToolset
skills = load_skills_from_dir(SKILLS_DIR)
skill_toolset = SkillToolset(skills=skills)

# Modelo e data atual
MODEL = os.getenv("MODEL", "gemini-3.8-flash")
TODAY = datetime.date.today().isoformat()

instruction = f"""Você é um mentor de estudos personalizado, atencioso e prático.
A data de hoje é {TODAY}.
O bucket do Google Cloud Storage para salvar e carregar os planos de estudo é '{GCS_BUCKET_NAME}'.

Seu objetivo é ajudar o estudante a montar um plano de estudos estruturado, com revisões espaçadas, checkpoints semanais e exportação da agenda para o Google Agenda (CSV).
Utilize a skill plano-de-estudos para conduzir a conversa, seguindo rigorosamente as regras de validação (gating) e os passos de planejamento."""

root_agent = Agent(
    # Keep in sync with create_params.root_agent_name in agents-cli-manifest.yaml
    name="agente_estudos",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[skill_toolset, gcs_toolset],
)

app = App(
    root_agent=root_agent,
    name="app",
)
