package com.tianji.aigc.service.impl;

import cn.hutool.core.date.DateUtil;
import com.tianji.aigc.config.SystemPromptConfig;
import com.tianji.aigc.domain.vo.ChatEventVO;
import com.tianji.aigc.enums.ChatEventTypeEnum;
import com.tianji.aigc.service.ChatService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.AbstractChatMemoryAdvisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements ChatService {

    private final ChatClient chatClient;
    private final ChatMemory chatMemory;
    private final SystemPromptConfig systemPromptConfig;
    private static final Map<String,Boolean> GENERATE_STATUS = new ConcurrentHashMap<>();

    @Override
    public Flux<ChatEventVO> chat(String question, String sessionId) {

        // 获取对话id
        var conversationId = ChatService.getConversationId(sessionId);
        // 大模型输出内容的缓存器，用于在输出中断后的数据存储
        StringBuilder outputBuilder = new StringBuilder();

        return this.chatClient
                .prompt()
                .system(promptSystem -> promptSystem
                        .text(systemPromptConfig.getChatSystemMessage().get())
                        .param("now", DateUtil.now()))
                // 设置会话ID，用于多轮对话
                .advisors(advisor->advisor.param(AbstractChatMemoryAdvisor.CHAT_MEMORY_CONVERSATION_ID_KEY,conversationId))
                .user(question)
                .stream()
                .chatResponse() // 获取响应流
                .doFirst(()->{GENERATE_STATUS.put(sessionId,true);})// 设置生成状态为true
                .doOnComplete(()->{GENERATE_STATUS.remove(sessionId);})// 生成完成后，设置生成状态为false
                .doOnError(throwable -> {GENERATE_STATUS.remove(sessionId);})// 生成异常后，设置生成状态为false
                .doOnCancel(()->{
                    this.saveStopHistoryRecord(conversationId,outputBuilder.toString());
                })
                // 根据生成状态控制流式输出，当状态为false时终止流
                .takeWhile(s ->
                        // 从并发缓存中获取当前会话的生成状态，若不存在则默认为false
                        Optional.ofNullable(GENERATE_STATUS.get(sessionId))
                                .orElse(false) // true:继续接收流数据，false:停止生成
                ) // 支持通过stop()方法主动中断AI回复流

                .map(chatResponse -> {
                    // 获取当前的输出内容
                    String text = chatResponse.getResult().getOutput().getText();
                    // 将当前的输出内容追加到缓存器中
                    outputBuilder.append(text);
                    return ChatEventVO.builder()
                            .eventData(text)
                            .eventType(ChatEventTypeEnum.DATA.getValue())
                            .build();
                })
                .concatWith(Flux.just(ChatEventVO.builder()
                        .eventType(ChatEventTypeEnum.STOP.getValue())
                        .build()));
    }

    private void saveStopHistoryRecord(String conversationId, String content) {
        this.chatMemory.add(conversationId,new AssistantMessage(content));
    }

    @Override
    public void stop(String sessionId) {
        GENERATE_STATUS.remove(sessionId);
    }
}
