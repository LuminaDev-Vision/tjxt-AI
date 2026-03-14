package com.tianji.aigc.service;


import com.tianji.aigc.domain.vo.ChatEventVO;
import com.tianji.common.utils.UserContext;
import reactor.core.publisher.Flux;

public interface ChatService {

    Flux<ChatEventVO> chat(String question,String sessionId);

    void stop(String sessionId);

    /**
     * 获取会话id
     * @param sessionId 会话id
     * @return 会话id
     */
    static String getConversationId(String sessionId){
        return UserContext.getUser() + "_" + sessionId;
    }

    String chatText(String question);
}
