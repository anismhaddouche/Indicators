from prefect import context

context.set("mon_nom", "Jean")

nom = context.get("mon_nom")
print(nom)