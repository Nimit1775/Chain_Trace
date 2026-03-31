import os
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")


SYSTEM_PROMPT = """You are ChainTrace AI, an expert cryptocurrency crime investigator.
You receive structured graph analysis data about a wallet and produce a concise, 
professional investigation report.

Your report must:
- Be 3-5 paragraphs
- Cite specific evidence from the data (risk score, cycles, clusters, pagerank)
- Explain WHY each finding is suspicious in plain English
- Conclude with a risk verdict: LOW / MEDIUM / HIGH / CRITICAL
- Sound like a real financial crime analyst wrote it

Do not use bullet points. Write in flowing paragraphs.
"""


def build_prompt(wallet_address: str, analysis: dict) -> str:
    return f"""Investigate this cryptocurrency wallet and write a report.

Wallet Address: {wallet_address}

Analysis Data:
- Risk Score: {analysis.get('risk_score', 'N/A')} / 100
- Flagged: {analysis.get('flagged', False)}
- Total Transactions: {analysis.get('tx_count', 0)}
- Total Sent: ${analysis.get('total_sent', 0):,.2f}
- Total Received: ${analysis.get('total_received', 0):,.2f}
- PageRank Centrality: {analysis.get('pagerank', 'N/A')} (higher = more central to network)
- Detected Cycles (circular flows): {len(analysis.get('cycles', []))} found
- Cycle Paths: {analysis.get('cycles', [])}
- Community Cluster ID: {analysis.get('cluster_id', 'None')} 
- Cluster Size: {analysis.get('cluster_size', 0)} wallets in same cluster
- Flagged Neighbor Count: {analysis.get('flagged_neighbors', 0)}

Write a professional investigation report:"""


async def generate_investigation_report(wallet_address: str, analysis: dict) -> str:
    prompt = build_prompt(wallet_address, analysis)

    if AI_PROVIDER == "gemini":
        return await _gemini(prompt)
    else:
        return await _openai(prompt)


async def _openai(prompt: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=600,
        temperature=0.4,
    )
    return response.choices[0].message.content


async def _gemini(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    response = await model.generate_content_async(prompt)
    return response.text
