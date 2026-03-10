package com.tianji.aigc.controller;

import com.tianji.aigc.domain.dto.ChatDTO;
import com.tianji.aigc.domain.vo.ChatEventVO;
import com.tianji.aigc.service.ChatService;
import com.tianji.common.annotations.NoWrapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@Slf4j
@RestController
@RequestMapping("/chat")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    @NoWrapper // 标记结果不进行包装
    @PostMapping
    public Flux<ChatEventVO> chat(@RequestBody ChatDTO chatDTO){
        return chatService.chat(chatDTO.getQuestion(),chatDTO.getSessionId());
    }

    @PostMapping("/stop")
    public void stop(@RequestParam("sessionId") String sessionId){
        this.chatService.stop(sessionId);
    }

}
