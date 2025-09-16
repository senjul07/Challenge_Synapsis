# soal1.py
import sys
import os

# Menambahkan path ke direktori parent untuk mengimpor modul callme
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import CrudHelper dari callme
from function.callme import CrudHelper

# Inisialisasi aplikasi Flask
app = CrudHelper.Flask("Challenge Synapsis.id")

# Menentukan port Flask
PORT = 8080


# Endpoint GET (read all nodes)
@app.route("/api/read/node", methods=["GET"])
def apiReadNode():
    nodes = CrudHelper.readAllNodes() # Baca semua node
    if nodes is False:
        return CrudHelper.makeResponse("Failed", "Error fetching data from database", [])
    return CrudHelper.makeResponse("Success", "Successfully fetched nodes", nodes)


# Endpoint POST (create node)
@app.route("/api/create/node", methods=["POST"])
def apiCreateNode():
    data = CrudHelper.request.get_json() # Ambil data JSON dari request
    name = data.get("name")
    if not name:
        return CrudHelper.makeResponse("Failed", "Name field required", [])

    success = CrudHelper.insertNode(name) # Insert node ke database
    nodes = CrudHelper.readAllNodes() # Baca semua node setelah insert
    status = "Success" if success else "Failed"
    message = "Node inserted successfully" if success else "Error inserting node"
    return CrudHelper.makeResponse(status, message, nodes)


# Endpoint PUT (update node)
@app.route("/api/update/node", methods=["PUT"])
def apiUpdateNode():
    data = CrudHelper.request.get_json() # Ambil data JSON dari request
    node_id = data.get("node_id") 
    name = data.get("name")

    if not node_id or not name: # Kalo field name atau node_id kosong
        return CrudHelper.makeResponse("Failed", "node_id and name required", [])

    success = CrudHelper.updateNode(node_id, name) # Update node di database

    if not success:
        return CrudHelper.makeResponse("Failed", "Error node_id doesnt exist", [])

    nodes = CrudHelper.readAllNodes() # Baca semua node setelah update
    return CrudHelper.makeResponse("Success", "Node updated successfully", nodes)


# Endpoint DELETE (delete node)
@app.route("/api/delete/node", methods=["DELETE"])
def apiDeleteNode():
    data = CrudHelper.request.get_json() # Ambil data JSON dari request
    node_id = data.get("node_id") 

    if not node_id: # Kalo field node_id kosong
        return CrudHelper.makeResponse("Failed", "node_id required", [])

    success = CrudHelper.deleteNode(node_id) # Delete node di database

    if not success:
        return CrudHelper.makeResponse("Failed", "Error node_id doesnt exist", [])

    nodes = CrudHelper.readAllNodes() # Baca semua node setelah delete
    return CrudHelper.makeResponse("Success", "Node deleted successfully", nodes)


# Menjalankan Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
