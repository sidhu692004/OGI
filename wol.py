# import wolframalpha

# # WolframAlpha API Key (अपने key से बदलो)
# APP_ID = "YG5T4TP5W3"

import wolframalpha

# अपने WolframAlpha API Key डालें
APP_ID = "YG5T4TP5W3"

def ask_wolfram(query):
    try:
        client = wolframalpha.Client(APP_ID)
        res = client.query(query)

        if res["@success"] == "false":
            return "I couldn't find an answer."

        # Safe way to get result
        results = list(res.results)
        if results:
            return results[0].text
        else:
            return "No direct answer found."
    
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("WolframAlpha Assistant")
    print("Type 'exit' to quit.\n")
    
    while True:
        q = input("Question: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("Answer:", ask_wolfram(q))
