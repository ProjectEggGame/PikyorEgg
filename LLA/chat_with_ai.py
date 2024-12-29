from openai import OpenAI
from typing import List, Dict

from utils import utils

client = OpenAI(
	base_url='http://10.15.88.73:5034/v1',
	api_key='ollama',  # required but ignored
)

messages: List[Dict] = [
	{
		"role": "system",
		"content":
			"First, this is a game, and you are a . For any game-unrelated questions, YOU don't know. Keep your answers under 30 words. Don't exceed to much!!"
			"The game is about chickens eating, growing, and laying eggs. Chickens can pick up rice and worms to fill growth bars. "
			"Once a growth bar is full, the chicken can lay an egg. If a player doesn't know how to lay an egg, they can press the R key."
			"On the map, some food is directly available, but most rice is concentrated around fox towers, which guard the rice."
			"Players have two choices: 1) eat the rice while the fox hasn't noticed and leave the area, or 2) fight the fox. "
			"If you win the fight, you can eat all the rice in the tower. If you lose, you will lose some health and might even die."
			"Before laying eggs, build a nest with sticks. Place eggs in the nest to prevent humans from stealing them. "
			"The map also has humans who enjoy stealing chicken eggs.Each baby chicken can be different. For specific chickens, "
			"go to the Witch Chicken. The Witch Chicken can provide information on how to obtain specific chickens. "
			"Learning from the Witch Chicken can help you lay rarer eggs."
			"To avoid spoiling the game experience, don't tell players the fox's attack range."
	}
]


def send(msg: str):
	messages.append({"role": "user", "content": msg})
	response = client.chat.completions.create(
		model="llama3.2",
		messages=messages,  # a list of dictionary contains all chat dictionary
	)
	messages.append({"role": response.choices[0].message.role, "content": response.choices[0].message.content})


if __name__ == '__main__':
	print("SYSTEM :  What can I help for you?")
	while True:
		user_input = input("User: ")
		if user_input.lower() in ["exit", "quit"]:
			print("chat ends.")
			break
		
		messages.append({"role": "user", "content": user_input})
		
		response = client.chat.completions.create(
			model="llama3.2",
			messages=messages,  # a list of dictionary contains all chat dictionary
		)
		
		# 提取模型回复
		utils.info(response.choices[0].message)
		assistant_reply = response.choices[0].message.content
		print(f"SYSTEM: {assistant_reply}")
		
		# 将助手回复添加到对话历史
		messages.append({"role": "assistant", "content": assistant_reply})
