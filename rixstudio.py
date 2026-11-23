import asyncio, json, mimetypes, os, uuid, urllib.error, urllib.request
from pathlib import Path
try:
    from .rixstudio_errors import APIError, NetworkError, UploadError
    from .rixstudio_models import Message, Update, InlineMessage, Track, Keypad, KeypadRow, Button
    from .rixstudio_queue import MusicQueue
except ImportError:
    from rixstudio_errors import APIError, NetworkError, UploadError
    from rixstudio_models import Message, Update, InlineMessage, Track, Keypad, KeypadRow, Button
    from rixstudio_queue import MusicQueue

class RixStudio:
    """Client for Rubika Bot API v3. Authentication is by bot token."""
    def __init__(self, token, base_url="https://botapi.rubika.ir/v3", timeout=30, poll_timeout=1, offset_id=None):
        if not isinstance(token, str) or not token.strip():
            raise ValueError("A valid Rubika bot token is required.")
        self.token, self.base_url, self.timeout = token.strip(), base_url.rstrip("/"), timeout
        self.poll_timeout, self.offset_id = poll_timeout, offset_id
        self.handlers, self.update_handlers, self.inline_handlers = [], [], []
        self.queue, self._running = MusicQueue(), False

    def _sync_request(self, method, payload=None):
        req = urllib.request.Request(
            f"{self.base_url}/{self.token}/{method}",
            data=json.dumps(payload or {}).encode(),
            headers={"Content-Type":"application/json","Accept":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                raw = r.read()
                try: data = json.loads(raw.decode("utf-8"))
                except Exception: data = {"raw": raw.decode("utf-8", "replace")}
                if not isinstance(data, dict): raise APIError("Unexpected API response", data, r.status)
                if data.get("status") in ("ERROR", "error", False):
                    raise APIError(str(data.get("error", data)), data, r.status)
                return data
        except urllib.error.HTTPError as e:
            try: body = json.loads(e.read().decode("utf-8"))
            except Exception: body = {}
            raise APIError(f"HTTP {e.code}: {body}", body, e.code) from e
        except urllib.error.URLError as e: raise NetworkError(str(e.reason)) from e

    async def _request(self, method, payload=None):
        return await asyncio.to_thread(self._sync_request, method, payload)

    @staticmethod
    def _put(dst, **kwargs):
        for k,v in kwargs.items():
            if v is not None: dst[k] = v.to_dict() if hasattr(v,"to_dict") else v

    @staticmethod
    def _find(data, key):
        if isinstance(data, dict):
            if key in data: return data[key]
            for v in data.values():
                found = RixStudio._find(v,key)
                if found is not None: return found
        elif isinstance(data,list):
            for v in data:
                found=RixStudio._find(v,key)
                if found is not None: return found
        return None

    async def get_me(self): return await self._request("getMe")
    async def get_chat(self, chat_id): return await self._request("getChat", {"chat_id":chat_id})
    async def send_message(self, chat_id, text, chat_keypad=None, disable_notification=None,
                           inline_keypad=None, reply_to_message_id=None, chat_keypad_type=None, metadata=None):
        p={"chat_id":chat_id,"text":text}
        self._put(p,chat_keypad=chat_keypad,disable_notification=disable_notification,
                  inline_keypad=inline_keypad,reply_to_message_id=reply_to_message_id,
                  chat_keypad_type=chat_keypad_type,metadata=metadata)
        return await self._request("sendMessage",p)
    async def send_poll(self, chat_id, question, options):
        return await self._request("sendPoll",{"chat_id":chat_id,"question":question,"options":options})
    async def send_location(self, chat_id, latitude, longitude, **kwargs):
        p={"chat_id":chat_id,"latitude":latitude,"longitude":longitude}; self._put(p,**kwargs)
        return await self._request("sendLocation",p)
    async def send_contact(self, chat_id, first_name, phone_number, last_name=None, **kwargs):
        p={"chat_id":chat_id,"first_name":first_name,"phone_number":phone_number}
        self._put(p,last_name=last_name,**kwargs); return await self._request("sendContact",p)
    async def get_updates(self, offset_id=None, limit=None):
        p={}; self._put(p,offset_id=self.offset_id if offset_id is None else offset_id,limit=limit)
        return await self._request("getUpdates",p)
    async def forward_message(self, from_chat_id, message_id, to_chat_id, disable_notification=None):
        p={"from_chat_id":from_chat_id,"message_id":message_id,"to_chat_id":to_chat_id}
        self._put(p,disable_notification=disable_notification); return await self._request("forwardMessage",p)
    async def edit_message_text(self, chat_id, message_id, text):
        return await self._request("editMessageText",{"chat_id":chat_id,"message_id":message_id,"text":text})
    async def edit_inline_keypad(self, chat_id, message_id, inline_keypad):
        return await self._request("editInlineKeypad",{"chat_id":chat_id,"message_id":message_id,"inline_keypad":inline_keypad})
    async def edit_message_keypad(self, chat_id, message_id, inline_keypad):
        return await self.edit_inline_keypad(chat_id,message_id,inline_keypad)
    async def delete_message(self, chat_id, message_id):
        return await self._request("deleteMessage",{"chat_id":chat_id,"message_id":message_id})
    async def set_commands(self, bot_commands):
        return await self._request("setCommands",{"bot_commands":bot_commands})
    async def update_bot_endpoints(self, url, type):
        return await self._request("updateBotEndpoints",{"url":url,"type":type})
    async def edit_chat_keypad(self, chat_id, chat_keypad_type, chat_keypad=None):
        p={"chat_id":chat_id,"chat_keypad_type":chat_keypad_type}; self._put(p,chat_keypad=chat_keypad)
        return await self._request("editChatKeypad",p)
    async def get_file(self, file_id): return await self._request("getFile",{"file_id":file_id})
    async def request_send_file(self, type): return await self._request("requestSendFile",{"type":type})

    def _multipart_upload(self, path, url):
        boundary="----RixStudio"+uuid.uuid4().hex
        name=os.path.basename(path); mime=mimetypes.guess_type(name)[0] or "application/octet-stream"
        with open(path,"rb") as f: content=f.read()
        head = (f"--{boundary}\\r\\n"
                f'Content-Disposition: form-data; name="file"; filename="{name}"\\r\\n'
                f"Content-Type: {mime}\\r\\n\\r\\n").encode()
        tail = f"\\r\\n--{boundary}--\\r\\n".encode()
        body = head + content + tail
        req=urllib.request.Request(url,data=body,headers={"Content-Type":f"multipart/form-data; boundary={boundary}"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r:
                raw=r.read()
                try: result=json.loads(raw.decode())
                except Exception: result={"raw":raw.decode("utf-8","replace")}
                fid=self._find(result,"file_id") or self._find(result,"id")
                if not fid: raise UploadError(f"file_id not found in upload response: {result}")
                return fid
        except Exception as e:
            if isinstance(e,UploadError): raise
            raise UploadError(str(e)) from e

    async def upload_file(self, file_path, file_type=None):
        path=Path(file_path)
        if not path.is_file(): raise FileNotFoundError(str(path))
        if file_type is None:
            ext=path.suffix.lower()
            file_type="Music" if ext==".mp3" else "Video" if ext==".mp4" else "Image" if ext in (".jpg",".jpeg",".png",".gif",".webp") else "File"
        ticket=await self.request_send_file(file_type)
        url=self._find(ticket,"upload_url")
        if not url: raise UploadError(f"upload_url missing: {ticket}")
        fid=await asyncio.to_thread(self._multipart_upload,str(path),url)
        return {"file_id":fid,"upload_response":ticket}

    async def send_file(self, chat_id, file, text=None, reply_to_message_id=None,
                        disable_notification=None, chat_keypad=None, inline_keypad=None, chat_keypad_type=None):
        fid=(await self.upload_file(file))["file_id"] if isinstance(file,(str,os.PathLike)) else (
            file.get("file_id") if isinstance(file,dict) else getattr(file,"file_id",None))
        if not fid: raise ValueError("file must be a path or an object containing file_id")
        p={"chat_id":chat_id,"file_id":fid}
        self._put(p,text=text,reply_to_message_id=reply_to_message_id,disable_notification=disable_notification,
                  chat_keypad=chat_keypad,inline_keypad=inline_keypad,chat_keypad_type=chat_keypad_type)
        return await self._request("sendFile",p)

    async def download_file(self,file_id,destination=None):
        info=await self.get_file(file_id); url=self._find(info,"download_url")
        if not url: raise APIError(f"download_url missing: {info}",info)
        destination=destination or file_id
        def download():
            with urllib.request.urlopen(url,timeout=self.timeout) as r, open(destination,"wb") as f: f.write(r.read())
        await asyncio.to_thread(download); return str(destination)

    async def ban_chat_member(self,chat_id,user_id):
        return await self._request("banChatMember",{"chat_id":chat_id,"user_id":user_id})
    async def unban_chat_member(self,chat_id,user_id):
        return await self._request("unbanChatMember",{"chat_id":chat_id,"user_id":user_id})

    def on_message(self, command=None, filters=None):
        def deco(fn): self.handlers.append((command,filters,fn)); return fn
        return deco
    def on_update(self, update_type=None):
        def deco(fn): self.update_handlers.append((update_type,fn)); return fn
        return deco
    def on_inline_message(self, fn=None):
        def deco(cb): self.inline_handlers.append(cb); return cb
        return deco(fn) if fn else deco

    async def _dispatch(self, raw):
        u=Update.from_dict(raw)
        for wanted,fn in self.update_handlers:
            if wanted is None or wanted==u.type: await self._invoke(fn,u)
        if u.type=="NewMessage" and u.new_message:
            m=Message(self,u.new_message,u.chat_id,u)
            for cmd,flt,fn in self.handlers:
                if cmd:
                    choices=cmd if isinstance(cmd,(tuple,list,set)) else [cmd]
                    if (m.text or "").split(" ",1)[0] not in choices: continue
                if flt and not flt(m): continue
                await self._invoke(fn,m)

    @staticmethod
    async def _invoke(fn,arg):
        result=fn(arg)
        if asyncio.iscoroutine(result): await result

    async def run_polling(self,limit=100,idle_sleep=0.5,stop_on_error=False):
        self._running=True
        while self._running:
            try:
                result=await self.get_updates(limit=limit)
                updates=self._find(result,"updates") or []
                nxt=self._find(result,"next_offset_id")
                if nxt is not None: self.offset_id=nxt
                for item in updates:
                    if isinstance(item,dict): await self._dispatch(item)
                if not updates: await asyncio.sleep(idle_sleep)
            except asyncio.CancelledError: raise
            except Exception:
                if stop_on_error: raise
                await asyncio.sleep(max(idle_sleep,1))
    def stop(self): self._running=False
    def run(self,**kwargs):
        try: asyncio.get_running_loop()
        except RuntimeError: return asyncio.run(self.run_polling(**kwargs))
        raise RuntimeError("Event loop active: use `await bot.run_polling()`.")

Bot=RixStudio
