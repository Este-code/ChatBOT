class ConversationBufferMemory:
    def __init__(self):
        self.buffer = []
    
    def add_memory(self, request, response):
        self.buffer.append([request, response])
    
    def get_memories(self):
        return self.buffer