from collections import defaultdict, deque
class MusicQueue:
    def __init__(self): self._queues=defaultdict(deque)
    def add(self,chat_id,track): self._queues[str(chat_id)].append(track); return len(self._queues[str(chat_id)])
    def next(self,chat_id):
        q=self._queues[str(chat_id)]; return q.popleft() if q else None
    def current(self,chat_id):
        q=self._queues[str(chat_id)]; return q[0] if q else None
    def all(self,chat_id): return list(self._queues[str(chat_id)])
    def clear(self,chat_id): self._queues[str(chat_id)].clear()
    def remove(self,chat_id,index):
        q=self._queues[str(chat_id)]
        if index<0 or index>=len(q): raise IndexError("queue index out of range")
        a=list(q); item=a.pop(index); self._queues[str(chat_id)]=deque(a); return item
    def __len__(self): return sum(map(len,self._queues.values()))
