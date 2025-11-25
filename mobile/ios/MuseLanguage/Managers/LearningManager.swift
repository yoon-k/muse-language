import Foundation
import SwiftUI
import Combine

@MainActor
class LearningManager: ObservableObject {
    // MARK: - Published Properties
    @Published var currentLevel: String = "A1"
    @Published var levelProgress: Double = 0
    @Published var totalXP: Int = 0
    @Published var weeklyXP: Int = 0

    @Published var currentStreak: Int = 0
    @Published var longestStreak: Int = 0
    @Published var lastStudyDate: Date?

    @Published var dailyProgress: DailyProgress = DailyProgress()
    @Published var dailyChallenges: [DailyChallenge] = []

    @Published var targetLanguage: String = "en"

    // MARK: - Computed Properties
    var streakIsActive: Bool {
        guard let lastDate = lastStudyDate else { return false }
        return Calendar.current.isDateInToday(lastDate) ||
               Calendar.current.isDateInYesterday(lastDate)
    }

    var xpForNextLevel: Int {
        let levels = ["A1": 500, "A2": 1000, "B1": 2000, "B2": 4000, "C1": 8000, "C2": 15000]
        return levels[currentLevel] ?? 500
    }

    // MARK: - Initialization
    init() {
        loadDailyChallenges()
    }

    // MARK: - XP Management
    func addXP(_ amount: Int) {
        totalXP += amount
        weeklyXP += amount
        dailyProgress.xpEarned += amount

        // Check level up
        checkLevelProgress()

        // Update streak
        updateStreak()

        // Check achievements
        checkAchievements()
    }

    private func checkLevelProgress() {
        let progress = Double(totalXP % xpForNextLevel) / Double(xpForNextLevel) * 100
        levelProgress = progress

        // Level up logic
        let levelThresholds: [(String, Int)] = [
            ("A1", 0),
            ("A2", 500),
            ("B1", 1500),
            ("B2", 3500),
            ("C1", 7500),
            ("C2", 15500)
        ]

        for (level, threshold) in levelThresholds.reversed() {
            if totalXP >= threshold {
                if currentLevel != level {
                    currentLevel = level
                    // Trigger level up celebration
                }
                break
            }
        }
    }

    // MARK: - Streak Management
    func updateStreak() {
        let today = Calendar.current.startOfDay(for: Date())

        if let lastDate = lastStudyDate {
            let lastDay = Calendar.current.startOfDay(for: lastDate)

            if Calendar.current.isDateInToday(lastDate) {
                // Already studied today
                return
            } else if Calendar.current.isDateInYesterday(lastDate) {
                // Continue streak
                currentStreak += 1
                if currentStreak > longestStreak {
                    longestStreak = currentStreak
                }
            } else {
                // Streak broken
                currentStreak = 1
            }
        } else {
            // First study
            currentStreak = 1
        }

        lastStudyDate = Date()
    }

    // MARK: - Daily Challenges
    private func loadDailyChallenges() {
        dailyChallenges = [
            DailyChallenge(id: "lesson", title: "레슨 1개 완료", target: 1, current: 0, xpReward: 20),
            DailyChallenge(id: "vocab", title: "단어 10개 복습", target: 10, current: 0, xpReward: 15),
            DailyChallenge(id: "conversation", title: "AI와 3회 대화", target: 3, current: 0, xpReward: 15),
            DailyChallenge(id: "pronunciation", title: "발음 연습 5회", target: 5, current: 0, xpReward: 15)
        ]
    }

    func updateChallenge(id: String, increment: Int = 1) {
        if let index = dailyChallenges.firstIndex(where: { $0.id == id }) {
            dailyChallenges[index].current += increment

            if dailyChallenges[index].isComplete {
                addXP(dailyChallenges[index].xpReward)
            }

            // Check if all challenges complete
            if dailyChallenges.allSatisfy({ $0.isComplete }) {
                addXP(50) // Bonus for completing all
            }
        }
    }

    // MARK: - Achievements
    private func checkAchievements() {
        // Check various achievement conditions
    }

    // MARK: - SRS (Spaced Repetition)
    func calculateNextReview(quality: Int, currentInterval: Int, easeFactor: Double) -> (interval: Int, ease: Double) {
        var newInterval: Int
        var newEase = easeFactor

        if quality < 3 {
            // Incorrect - reset
            newInterval = 1
        } else {
            // Correct
            if currentInterval == 0 {
                newInterval = 1
            } else if currentInterval == 1 {
                newInterval = 6
            } else {
                newInterval = Int(Double(currentInterval) * easeFactor)
            }

            // Update ease factor
            newEase = easeFactor + (0.1 - Double(5 - quality) * (0.08 + Double(5 - quality) * 0.02))
            newEase = max(1.3, min(2.5, newEase))
        }

        return (min(newInterval, 365), newEase)
    }
}

// MARK: - Daily Progress
struct DailyProgress {
    var studyMinutes: Int = 0
    var lessonsCompleted: Int = 0
    var wordsReviewed: Int = 0
    var xpEarned: Int = 0
    var conversationCount: Int = 0

    var dailyGoalProgress: Double {
        let goal = 50 // Daily XP goal
        return min(Double(xpEarned) / Double(goal) * 100, 100)
    }
}

// MARK: - Auth Manager
@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?

    func login(email: String, password: String) async throws {
        // API call
        isAuthenticated = true
    }

    func register(email: String, password: String, name: String) async throws {
        // API call
        isAuthenticated = true
    }

    func logout() {
        isAuthenticated = false
        currentUser = nil
    }
}
