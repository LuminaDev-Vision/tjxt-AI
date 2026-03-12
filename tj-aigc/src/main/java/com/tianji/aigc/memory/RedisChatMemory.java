package com.tianji.aigc.memory;

import cn.hutool.core.collection.CollStreamUtil;

import com.tianji.common.utils.CollUtils;
import jakarta.annotation.Resource;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.messages.Message;

import org.springframework.data.redis.core.StringRedisTemplate;

import java.util.List;

public class RedisChatMemory implements ChatMemory {

    private static final String DEFAULT_PREFIX = "chat:";

    private final String prefix;

    public RedisChatMemory() {
        this.prefix = DEFAULT_PREFIX;
    }

    public RedisChatMemory(String prefix) {
        this.prefix = prefix;
    }

    @Resource
    private  StringRedisTemplate stringRedisTemplate;



    @Override
    public void add(String conversationId, List<Message> messages) {
        if(CollUtils.isEmpty(messages) ){
            return;
        }
        var key = this.getKey(conversationId);
        var listOps = this.stringRedisTemplate.boundListOps(key); // 绑定到一个 List 类型的 key
        messages.forEach(message -> {
            listOps.rightPush(MessageUtil.toJson(message)); // 将消息序列化为 JSON 字符串并添加到 List 的右侧
        });
    }

    private String getKey(String conversationId) {
        return prefix + conversationId;
    }

    @Override
    public List<Message> get(String conversationId, int lastN) {
        if (lastN <= 0){
            return List.of();
        }
        // 生成Redis键名用于存储会话消息
        var redisKey = this.getKey(conversationId);
        // 获取Redis列表操作对象
        var listOps = this.stringRedisTemplate.boundListOps(redisKey);

        // 从Redis列表中获取指定范围的元素（从第一个元素开始到lastN位置）
        var messages = listOps.range(0, lastN);
        // 将Redis返回的字符串列表转换为Message对象列表
        return CollStreamUtil.toList(messages, MessageUtil::toMessage);

    }

    @Override
    public void clear(String conversationId) {
        String redisKey = this.getKey(conversationId);
        this.stringRedisTemplate.delete(redisKey);
    }

    /**
     * 根据对话ID优化对话记录，删除最后的2条消息，因为这2条消息是从路由智能体存储的，请求由后续的智能体处理
     * 为了确保历史消息的完整性，所以需要将中间转发的消息清理掉
     *
     * @param conversationId 对话的唯一标识符
     */
    public void optimization(String conversationId) {
        var redisKey = this.getKey(conversationId);
        var listOps = this.stringRedisTemplate.boundListOps(redisKey);
        // 从Redis列表右侧弹出2个元素
        listOps.rightPop(2);
    }
}
