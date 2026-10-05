from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer("all-MiniLM-L6-v2")

sentence_a = (
    "Client production workloads belong in the "
    "SirhurryUp Managed Websites account."
)

sentence_b = (
    "Customer websites should be deployed to the account "
    "reserved for managed client workloads."
)

sentence_c = (
    "Chocolate cake tastes better with vanilla frosting."
)

embedding_a = model.encode(sentence_a)
embedding_b = model.encode(sentence_b)
embedding_c = model.encode(sentence_c)

similar_ab = cos_sim(embedding_a, embedding_b)
similar_ac = cos_sim(embedding_a, embedding_c)

print("A vs B:", similar_ab.item())
print("A vs C:", similar_ac.item())