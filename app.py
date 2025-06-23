import sys
from agent.agent_runner import answer_question

print("neo4j ai assistant")
print("ask questions about people, countries, and products")
print("-" * 50)

# handle command line argument or prompt for input
if len(sys.argv) > 1:
    question = " ".join(sys.argv[1:])
    print(f"your question: {question}")
else:
    question = input("your question: ")

print()
print(answer_question(question)) 