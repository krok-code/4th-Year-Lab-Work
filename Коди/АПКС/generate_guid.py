import hashlib
import uuid

full_name = "Смолінський Максим Володимирович"

hash_object = hashlib.md5(full_name.encode('utf-8'))
hash_hex = hash_object.hexdigest()

generated_guid = str(uuid.UUID(hash_hex))

print("=" * 50)
print(f"Студент: {full_name}")
print(f"Згенерований GUID: {generated_guid}")
print("=" * 50)