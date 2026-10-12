from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"
system_msg = """You are a helpful assistant."""

def extract_text(response):
    for block in response.content:
        if block.type == "text":
            return block.text

    return "No text response returned."

def ask(question, system=system_msg):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    usage=response.usage
    print(f"[tokens in: {usage.input_tokens}, out: {usage.output_tokens}]")
    return extract_text(response)

if __name__ == "__main__":
    print(ask("What was the UK Bank Rate in March 2023, and how many mortgage approvals were there that month?"))