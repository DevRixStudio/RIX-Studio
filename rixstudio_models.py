from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Track:
    title: str
    file_id: Optional[str]=None
    url: Optional[str]=None
    duration: Optional[int]=None
    artist: Optional[str]=None
    metadata: dict=field(default_factory=dict)

@dataclass
class Button:
    id: str
    type: str
    button_text: str
    extra: dict=field(default_factory=dict)
    def to_dict(self):
        d={"id":self.id,"type":self.type,"button_text":self.button_text}; d.update(self.extra); return d

@dataclass
class KeypadRow:
    buttons: list
    def to_dict(self): return {"buttons":[b.to_dict() if hasattr(b,"to_dict") else b for b in self.buttons]}

@dataclass
class Keypad:
    rows: list
    resize_keyboard: bool=True
    one_time_keyboard: bool=False
    def to_dict(self):
        return {"rows":[r.to_dict() if hasattr(r,"to_dict") else r for r in self.rows],
                "resize_keyboard":self.resize_keyboard,"one_time_keyboard":self.one_time_keyboard}

@dataclass
class Update:
    raw: dict
    type: Optional[str]=None
    chat_id: Optional[str]=None
    new_message: Optional[dict]=None
    updated_message: Optional[dict]=None
    removed_message_id: Optional[str]=None
    event_data: Optional[dict]=None
    @classmethod
    def from_dict(cls,d):
        return cls(d,d.get("type"),d.get("chat_id"),d.get("new_message"),d.get("updated_message"),
                   d.get("removed_message_id"),d.get("event_data"))

class Message:
    def __init__(self,bot,data,chat_id=None,update=None):
        self.bot,self.raw,self.update=bot,data or {},update
        for k in ("chat_id","message_id","text","time","is_edited","sender_type","sender_id","aux_data",
                  "file","reply_to_message_id","forwarded_from","location","sticker","contact_message","poll"):
            setattr(self,k,self.raw.get(k) or (chat_id if k=="chat_id" else "" if k=="text" else None))
    async def reply(self,text,**kwargs):
        return await self.bot.send_message(self.chat_id,text,reply_to_message_id=self.message_id,**kwargs)
    answer=reply
    async def edit(self,text): return await self.bot.edit_message_text(self.chat_id,self.message_id,text)
    async def delete(self): return await self.bot.delete_message(self.chat_id,self.message_id)
    async def send_file(self,file,**kwargs): return await self.bot.send_file(self.chat_id,file,**kwargs)

@dataclass
class InlineMessage:
    raw: dict
    sender_id: Optional[str]=None
    text: str=""
    file: Optional[dict]=None
    location: Optional[dict]=None
    aux_data: Optional[dict]=None
    message_id: Optional[str]=None
    chat_id: Optional[str]=None
    @classmethod
    def from_dict(cls,d):
        return cls(d,d.get("sender_id"),d.get("text",""),d.get("file"),d.get("location"),
                   d.get("aux_data"),d.get("message_id"),d.get("chat_id"))
