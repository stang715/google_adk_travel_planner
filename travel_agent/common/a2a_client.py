
"""
This lightweight async utility allows any agent (especially the host) 
to invoke another agent using the A2A protocol by calling the /run endpoint.
"""

import httpx
async def call_agent(url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()
    


