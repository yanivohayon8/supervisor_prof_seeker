import lunary
from langchain_openai import ChatOpenAI

class ThreadWrapper():

    def __init__(self,thread_id:str=None,tags:list[str]=None,**kwargs):
        self.thread = lunary.open_thread(id=thread_id,tags=tags,**kwargs)
        self.msgs_ids = []

    def num_saved_msgs_(self):
        return len(self.msgs_ids)

    def last_msg_id_(self):
        if self.num_saved_msgs_() == 0:
            return None
        
        return self.msgs_ids[-1]

    def save_msg_(self,msg_id):
        self.msgs_ids.append(msg_id)

    def track_user(self, content):
        if self.num_saved_msgs_() == 0:
            msg_id = self.thread.track_message({"role":"user", "content":content})
        else:
            last_msg = self.last_msg_id_()
            with lunary.parent(last_msg):
                msg_id = self.thread.track_message({"role":"user", "content":content})

        self.save_msg_(msg_id)
    
    def track_assistant(self,llm:ChatOpenAI,invoke_input:str,invoke_params:dict={}):
        '''
            llm - should be initialize with the right callbacks value (use src.api_utils.get_langchain_openai_lunary_)
        '''
        if self.num_saved_msgs_() == 0:
            response = llm.invoke(invoke_input,**invoke_params)
            msg_id = self.thread.track_message({"role":"assistant", "content":response.content})
        else:
            last_msg = self.last_msg_id_()
            with lunary.parent(last_msg):
                # The llm.invoke must be in the context of lunary.parent to trace properly
                response = llm.invoke(invoke_input,**invoke_params) 
                msg_id = self.thread.track_message({"role":"assistant", "content":response.content})

        self.save_msg_(msg_id)

        return response

    def feedback_on_message_(self,msg_id:str,thumb:str):
        lunary.track_feedback(msg_id, {"thumb":thumb})

    def positive_feedback(self,msg_id:str):
        self.feedback_on_message_(msg_id,"up")
    
    def negative_feedback(self,msg_id:str):
        self.feedback_on_message_(msg_id,"down")
    
    def delete_feedback(self,msg_id:str):
        self.feedback_on_message_(msg_id,None)

    def track_retriever(self,documents:list[str]):
        # https://docs.lunary.ai/docs/features/conversations#python
        #  The supported roles are assistant, user, system, & tool
        raise NotImplementedError()
        # for doc in documents:
        #     self.thread.track_message({"role: retriever",},user_id=)

