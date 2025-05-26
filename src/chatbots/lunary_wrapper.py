import lunary
from langchain_openai import ChatOpenAI

class ConversationRecorder():

    def __init__(self,thread_id:str=None,tags:list[str]=None,**kwargs):
        self.thread = lunary.open_thread(id=thread_id,tags=tags,**kwargs)
        self.msgs_ids = ["_"]
        self.msgs_data = [{"role":"assistant", "content":"Let's start chatting! 👇"}]

    def num_saved_msgs_(self):
        return len(self.msgs_ids)

    def last_msg_id_(self):
        if self.num_saved_msgs_() == 0:
            return None
        
        return self.msgs_ids[-1]

    def save_msg_(self,msg_id:str,data:dict):
        self.msgs_ids.append(msg_id)
        self.msgs_data.append(data)

    def track_user(self, user_input:str):
        data = {"role":"user", "content":user_input}

        if self.num_saved_msgs_() == 0:
            msg_id = self.thread.track_message(data)
        else:
            last_msg = self.last_msg_id_()
            with lunary.parent(last_msg):
                msg_id = self.thread.track_message(data)

        self.save_msg_(msg_id,data)
    
    def track_assistant(self,llm:ChatOpenAI,user_input:str,invoke_params:dict={}):
        '''
            llm - should be initialize with the right callbacks value (use src.api_utils.get_langchain_openai_lunary_)
        '''

        if self.num_saved_msgs_() == 0:
            response = llm.invoke(user_input,**invoke_params)
            data = {"role":"assistant", "content":response.content}
            msg_id = self.thread.track_message(data)
        else:
            last_msg = self.last_msg_id_()
            with lunary.parent(last_msg):
                # The llm.invoke must be in the context of lunary.parent to trace properly
                response = llm.invoke(user_input,**invoke_params) 
                data = {"role":"assistant", "content":response.content}
                msg_id = self.thread.track_message(data)

        self.save_msg_(msg_id,data)

        return response

    def feedback_on_message_(self,msg_id:str,thumb:str):
        lunary.track_feedback(msg_id, {"thumb":thumb})

    def positive_feedback_(self,msg_id:str):
        self.feedback_on_message_(msg_id,"up")
    
    def positive_feedback(self,msg_index:int):
        msg_id = self.msgs_ids[msg_index]
        self.positive_feedback_(msg_id)

    def positive_feedback_last_message(self):
        self.positive_feedback_(self.last_msg_id_())
    
    def negative_feedback_(self,msg_id:str):
        self.feedback_on_message_(msg_id,"down")

    def negative_feedback(self,msg_index:int):
        msg_id = self.msgs_ids[msg_index]
        self.negative_feedback_(msg_id)
    
    def negative_feedback_last_message(self):
        self.negative_feedback_(self.last_msg_id_())
    
    def delete_feedback_(self,msg_id:str):
        self.feedback_on_message_(msg_id,None)

    def delete_feedback(self,msg_index:int):
        msg_id = self.msgs_ids[msg_index]
        self.delete_feedback_(msg_id)

    def track_retriever(self,documents:list[str]):
        # https://docs.lunary.ai/docs/features/conversations#python
        #  The supported roles are assistant, user, system, & tool
        raise NotImplementedError()
        # for doc in documents:
        #     self.thread.track_message({"role: retriever",},user_id=)

