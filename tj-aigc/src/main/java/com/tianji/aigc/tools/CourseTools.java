package com.tianji.aigc.tools;

import com.tianji.aigc.constants.Constant;
import com.tianji.aigc.tools.result.CourseInfo;
import com.tianji.api.client.course.CourseClient;
import lombok.RequiredArgsConstructor;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.util.Optional;

/**
 * 课程工具类
 */
@Component
@RequiredArgsConstructor
public class CourseTools {

    private final CourseClient courseClient;

    /**
     * 根据课程id查询课程信息
     * @param courseId 课程id
     * @return 课程信息实体对象
     */
    @Tool(description = Constant.Tools.QUERY_COURSE_BY_ID)
    public CourseInfo queryCourseById(@ToolParam(description = Constant.ToolParams.COURSE_ID) Long courseId){
        return Optional.ofNullable(courseId)
                .map(id->CourseInfo.of(this.courseClient.baseInfo(courseId,true)))
                .orElse(null);
    }

}
