
class JsonCircuit(dict):
    
    @staticmethod
    def get_path_from_stem(paths):
        result = []
        for fingerprint, name in paths:
            path = {
                'fingerprint': fingerprint,
                'name': name
            }
            result.append(path)
        return result
        
    @staticmethod
    def get_path_from_txtor(path):
        result = []
        for router in path:
            result.append({
                        'fingerprint': router.unique_name,
                        'name': router.name
                    })
        return result

    @staticmethod
    def from_stem(circuit):
        d = JsonCircuit()
        d['id'] = circuit.id
        d['status'] = circuit.status
        d['path'] = JsonCircuit.get_path_from_stem(circuit.path)
        return d

    @staticmethod
    def from_txtor(circuit):
        d = JsonCircuit()
        d['id'] = circuit.id
        d['status'] = circuit.state
        d['purpose'] = circuit.purpose
        d['path'] = JsonCircuit.get_path_from_txtor(circuit.path)
        return d
