from agent.agent_runner import answer_question

print("neo4j ai assistant")
print("ask questions about people, countries, and products")
print("-" * 50)

question = input("your question: ")
print()
print(answer_question(question)) 