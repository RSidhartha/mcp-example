# Answers: Build and Call Your Own MCP Tool

## 1. How many tools, and what changed in the client?

In Part 1 the demo client reported **8 tools**. In Part 3 my client reported **9 tools**. The new one was `predict_both`.

I didn't change anything in the client to make the new tool appear. The only change was on the server: I added the `predict_both` function with the `@server.tool()` decorator to `mcp_ml_server.py`. When the client starts, it calls `server.list_tools()` (MCP's `tools/list` request), and the server replies with every tool it currently offers. The client doesn't have a hard-coded list of tools. It discovers them at runtime, so any tool added to the server shows up automatically.

## 2. On how many patients do the models disagree, and which model was right?

The models disagree on **8 of the 114** test patients.

| Patient | True diagnosis | Logistic regression | KNN | Model that was right |
|---|---|---|---|---|
| 3 | benign | benign | malignant | Logistic regression |
| 25 | benign | benign | malignant | Logistic regression |
| 48 | benign | benign | malignant | Logistic regression |
| 53 | malignant | benign | malignant | KNN |
| 76 | malignant | malignant | benign | Logistic regression |
| 80 | benign | benign | malignant | Logistic regression |
| 99 | benign | benign | malignant | Logistic regression |
| 102 | malignant | malignant | benign | Logistic regression |

## 3. Which model was right more often when they disagreed?

**Logistic regression** was right in 7 of the 8 disagreements. KNN was right only once (patient 53).

Most of KNN's mistakes were false alarms: in 5 of the 8 cases it called a benign patient malignant. It also missed 2 malignant cases (patients 76 and 102) that logistic regression caught. Logistic regression's one mistake (patient 53) was a missed malignant case, which is the more serious type of error in cancer screening, but overall it was clearly the more reliable model. This matches the overall test metrics from `confusion_matrix_metrics`: logistic regression had 96.5% accuracy and 92.9% recall on the malignant class, compared with 91.2% and 90.5% for KNN.

A likely reason KNN does worse is that it compares patients by raw distance and the features are not scaled. Features like `worst area` and `mean area` are in the hundreds or thousands, while features like smoothness are around 0.1, so the large features dominate the distance and the small ones barely count.

## 4. Why does the description in triple quotes matter?

When the server lists its tools, the docstring is sent as the tool's description, together with its name and input schema. An AI app never sees the Python code inside the function. The description is the only thing it has to decide whether this tool fits what the user asked for and how to call it. A clear description like "Predict with BOTH models in one call and report whether they agree" tells the AI exactly when to use `predict_both` instead of calling the two single-model tools separately. If the description were vague or missing, the AI could skip a useful tool, pick the wrong one, or pass the wrong inputs. In a sense, the docstring is a prompt written for the AI. The `Field(description=...)` on `input_data` works the same way: it tells the AI what format the patient data needs to be in.

## 5. Why is it useful for the server to log every tool call?

An AI client decides on its own which tools to call, so no human necessarily sees each request. The audit log is the record of what actually happened: which tool ran, with which request ID, and whether it succeeded. This gives accountability, which matters a lot when the tools make medical predictions. If a prediction is questioned later, you can trace which tool and model produced it and when.

The log also helps with debugging. Failed calls are recorded with their status, and the `request_id` lets you trace a specific call, such as `hw-both-113`, back to the exact patient it was for. It supports monitoring and security too: you can see which tools are used most, notice errors piling up, or catch an AI calling tools it shouldn't or calling them far more often than expected. Finally, because the logging happens on the server inside `_run`, every call from every client is recorded the same way, without each client having to remember to log anything.
