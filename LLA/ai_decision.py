from typing import List, Dict

import LLA.chat_with_ai as ai
from utils.util import utils
from window.input import asyncTasks

properties = []


def asyncProperties(keywords: list[str]):
	asyncTasks.create_task(getProperties(keywords))


async def getProperties(keywords: List[str]):
	msg = [
		{
			"role": "user",
			"content":
				f"You have the styles with its serial number: "
				f"1: starry, 2: angel, 3: demon, 4: runic, ; "
				f"and you have the keywords: "
				f"{keywords}. "
				f"Decide what styles match the keywords. "
				f"You can choose more than one styles. "
				f"Only reply me the serial numbers, divide them with a single space."
		}
	]
	while True:
		response = ai.client.chat.completions.create(
			model="llama3.2",
			messages=msg  # a list of dictionary contains all chat dictionary
		)
		content = response.choices[0].message.content
		utils.info(content)
		lst = content.split(' ')
		new = []
		for i in lst:
			try:
				i = int(i.strip())
			except Exception as _:
				break
			new.append(i)
		else:
			break
	global properties
	properties = new
