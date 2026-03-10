package com.tianji.aigc.controller;

import com.tianji.aigc.service.ChatSessionService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/session")
@RequiredArgsConstructor
public class SessionController {

    private final ChatSessionService chatSessionService;

    @PostMapping
    public com.tianji.aigc.vo.SessionVO createSession(@RequestParam(value = "n", defaultValue = "3") Integer num) {
        return chatSessionService.createSession(num);
    }

    @GetMapping("/hot")
    public List<com.tianji.aigc.vo.SessionVO.Example> getHotQuestions(@RequestParam(value = "n", defaultValue = "3") Integer num){
        return chatSessionService.getHotQuestions(num);
    }
}
