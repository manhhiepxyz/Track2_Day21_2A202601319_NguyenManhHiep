import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

train_df = pd.read_csv("data/train_phase1.csv")
eval_df = pd.read_csv("data/eval.csv")

X_train = train_df.drop("target", axis=1)
y_train = train_df["target"]
X_eval = eval_df.drop("target", axis=1)
y_eval = eval_df["target"]

best_acc = 0
best_params = {}

for n in [100, 200, 300, 500]:
    for d in [None, 10, 20, 30]:
        for s in [2, 5, 10]:
            clf = RandomForestClassifier(n_estimators=n, max_depth=d, min_samples_split=s, random_state=42)
            clf.fit(X_train, y_train)
            acc = accuracy_score(y_eval, clf.predict(X_eval))
            if acc > best_acc:
                best_acc = acc
                best_params = {"n_estimators": n, "max_depth": d, "min_samples_split": s}
            if acc >= 0.68:
                print(f"Found! Acc: {acc:.4f} | Params: {n}, {d}, {s}")

print(f"Best: {best_acc:.4f} | Params: {best_params}")
