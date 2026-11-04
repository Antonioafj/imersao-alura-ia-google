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

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.apps import App
from google.adk.environment import LocalEnvironment
from google.adk.models import Gemini
from google.adk.skills import load_skills_from_dir
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.environment import EnvironmentToolset
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types


class FileOnlyEnvironmentToolset(EnvironmentToolset):
    """EnvironmentToolset that restricts exposed tools to only ReadFile and WriteFile."""

    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> list[BaseTool]:
        tools = await super().get_tools(readonly_context)
        return [t for t in tools if t.name in ("ReadFile", "WriteFile")]


# Diretórios do projeto
APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
SKILLS_DIR = APP_DIR / "skills"
PLANOS_DIR = PROJECT_DIR / "planos"
PLANOS_DIR.mkdir(parents=True, exist_ok=True)

# Configuração do LocalEnvironment e EnvironmentToolset restrito
local_env = LocalEnvironment(working_dir=PLANOS_DIR)
env_toolset = FileOnlyEnvironmentToolset(environment=local_env)

# Carregamento das ADK Skills com SkillToolset
skills = load_skills_from_dir(SKILLS_DIR)
skill_toolset = SkillToolset(skills=skills)

# Modelo e data atual
MODEL = os.getenv("MODEL", "gemini-3.8-flash")
TODAY = datetime.date.today().isoformat()

instruction = f"""Você é um mentor de estudos personalizado, atencioso e prático.
A data de hoje é {TODAY}.

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
    tools=[skill_toolset, env_toolset],
)

app = App(
    root_agent=root_agent,
    name="app",
)
