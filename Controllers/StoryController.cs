using Microsoft.AspNetCore.Mvc;
using PrivateSekai.Crypto;
using PrivateSekai.Models;
using PrivateSekai.Services;

namespace PrivateSekai.Controllers;

[ApiController]
public class StoryController : PrskController
{
    private readonly UserManager _users;

    public StoryController(UserManager users)
    {
        _users = users;
    }

    /// <summary>
    /// POST /api/user/{userId}/story/special_story/episode/{episodeId}
    /// </summary>
    [HttpPost("api/user/{userId}/story/special_story/episode/{episodeId}")]
    public IActionResult HandleSpecialStoryEpisode(long userId, int episodeId)
    {
        var user = _users.GetUser(userId);
        user.ReadEpisode(episodeId);
        user.UpdateRefreshableTypes("userSpecialEpisodeStatuses");

        var responseData = new UserStoryResponse
        {
            updatedResources = user.GetRefreshData(
                deleteRtypes: new HashSet<string> { "userBeginnerMissionBehavior" }),
            userObtainResourceResults = []
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// GET /api/user/{userId}/story/recommend
    /// </summary>
    [HttpGet("api/user/{userId}/story/recommend")]
    public IActionResult HandleStoryRecommend(long userId)
    {
        var responseData = new UserStoryRecommendResponse
        {
            userStoryRecommends =
            [
                new UserStoryRecommend
                {
                    storyType = "unit_story",
                    storyId = 10,
                    reason = "continuously",
                    category = "continuously",
                    seq = 1
                },
                new UserStoryRecommend
                {
                    storyType = "unit_story",
                    storyId = 9,
                    reason = "main_story",
                    category = "random",
                    seq = 2
                },
                new UserStoryRecommend
                {
                    storyType = "event_story",
                    storyId = 27,
                    reason = "recommend",
                    category = "random",
                    seq = 3
                }
            ]
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// GET /api/user/{userId}/story-favorite/friend/status/{storyType}
    /// </summary>
    [HttpGet("api/user/{userId}/story-favorite/friend/status/{storyType}")]
    public IActionResult HandleStoryFavoriteFriendStatus(long userId, string storyType)
    {
        var responseData = new StoryFavoriteFriendStatusResponse
        {
            friendStoryFavoriteStatuses = []
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// GET /api/user/{userId}/story-episode-bookmark/{storyType}/story/{storyId}
    /// </summary>
    [HttpGet("api/user/{userId}/story-episode-bookmark/{storyType}/story/{storyId}")]
    public IActionResult HandleStoryEpisodeBookmark(long userId, string storyType, int storyId)
    {
        var responseData = new StoryEpisodeBookmarkResponse
        {
            userStoryEpisodeBookmarks = []
        };
        return PrskResponse(responseData);
    }

    /// <summary>
    /// POST /api/user/{userId}/story/archive_event_story/episode/{episodeId}/log
    /// </summary>
    [HttpPost("api/user/{userId}/story/archive_event_story/episode/{episodeId}/log")]
    public IActionResult HandleArchiveEventStoryEpisodeLog(long userId, int episodeId)
    {
        var user = _users.GetUser(userId);
        var responseData = new UserStoryResponse
        {
            updatedResources = user.GetRefreshData(
                deleteRtypes: new HashSet<string> { "userBeginnerMissionBehavior" }),
            userObtainResourceResults = []
        };
        return PrskResponse(responseData);
    }
}
