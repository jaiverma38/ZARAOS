import json
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class LlmEngine:
    def __init__(self, model_name: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype, device_map="auto", trust_remote_code=True)

    def chat(self, text: str, locale: str, memories: list[str] | None = None) -> str:
        system = "You are Zara, a warm robot companion. Reply in Hindi, English, or Hinglish matching the user. Be concise and actionable."
        context = "\n".join(memories or [])
        messages = [{"role": "system", "content": system + "\nMemory:\n" + context}, {"role": "user", "content": text}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=256, temperature=0.6, do_sample=True)
        return self.tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True).strip()

    def intent(self, text: str, locale: str) -> dict:
        prompt = (
            "Return only JSON for a robot command. Supported actions: move, follow_user, come_here, go_back, "
            "rotate, return_home, stop, speak, relay. Include intent, action, confidence, direction, speed, duration_ms when useful.\n"
            f"User ({locale}): {text}"
        )
        raw = self.chat(prompt, locale)
        match = re.search(r"\{.*\}", raw, re.S)
        if match:
            return json.loads(match.group(0))
        lowered = text.lower()
        if "paas" in lowered or "come" in lowered:
            return {"intent": "robot_move", "action": "come_here", "confidence": 0.72}
        if "follow" in lowered or "mere peeche" in lowered:
            return {"intent": "robot_move", "action": "follow_user", "confidence": 0.72}
        return {"intent": "chat", "action": "speak", "confidence": 0.5, "text": raw}
