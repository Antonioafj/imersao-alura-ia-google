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

import pytest
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import Capabilities
from google.adk.tools.skill_toolset import SkillToolset

from app.agent import GCS_BUCKET_NAME, gcs_toolset, root_agent


def test_root_agent_toolsets() -> None:
    """Verifies root_agent is equipped with SkillToolset and GCSToolset."""
    toolsets = root_agent.tools
    assert len(toolsets) == 2

    skill_toolsets = [t for t in toolsets if isinstance(t, SkillToolset)]
    gcs_toolsets = [t for t in toolsets if isinstance(t, GCSToolset)]

    assert len(skill_toolsets) == 1, "Expected exactly one SkillToolset"
    assert len(gcs_toolsets) == 1, "Expected exactly one GCSToolset"


def test_gcs_toolset_settings() -> None:
    """Verifies GCSToolset is configured with READ_WRITE capabilities."""
    settings = gcs_toolset._tool_settings
    assert settings is not None
    assert Capabilities.READ_WRITE in settings.capabilities


@pytest.mark.asyncio
async def test_gcs_toolset_tools() -> None:
    """Verifies GCSToolset exposes expected filtered tools."""
    tools = await gcs_toolset.get_tools()
    tool_names = [tool.name for tool in tools]

    assert "create_object" in tool_names
    assert "get_object_data" in tool_names
    assert "list_objects" in tool_names
    assert "delete_objects" not in tool_names


def test_instruction_contains_gcs_bucket() -> None:
    """Verifies root_agent instruction references the GCS bucket."""
    assert GCS_BUCKET_NAME in root_agent.instruction
