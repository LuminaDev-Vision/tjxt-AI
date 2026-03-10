package com.tianji.aigc.service;

import com.tianji.aigc.domain.dto.ChatDTO;
import com.tianji.aigc.domain.vo.ChatEventVO;
import reactor.core.publisher.Flux;

public interface ChatService {

    Flux<ChatEventVO> chat(String question,String sessionId);

}
