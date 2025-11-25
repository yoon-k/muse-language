import Foundation
import SwiftData

// MARK: - User Model
@Model
final class User {
    @Attribute(.unique) var id: String
    var email: String
    var name: String
    var nativeLanguage: String
    var isPremium: Bool
    var createdAt: Date

    @Relationship(deleteRule: .cascade)
    var profiles: [LearningProfile]

    init(
        id: String = UUID().uuidString,
        email: String,
        name: String,
        nativeLanguage: String = "ko",
        isPremium: Bool = false,
        createdAt: Date = Date()
    ) {
        self.id = id
        self.email = email
        self.name = name
        self.nativeLanguage = nativeLanguage
        self.isPremium = isPremium
        self.createdAt = createdAt
        self.profiles = []
    }
}

// MARK: - Learning Profile
@Model
final class LearningProfile {
    @Attribute(.unique) var id: String
    var targetLanguage: String
    var currentLevel: String
    var levelProgress: Double

    var totalStudyTime: Int // minutes
    var totalLessons: Int
    var totalWordsLearned: Int
    var currentStreak: Int
    var longestStreak: Int
    var lastStudyDate: Date?

    var totalXP: Int
    var weeklyXP: Int

    @Relationship(deleteRule: .cascade)
    var vocabulary: [VocabularyWord]

    var user: User?

    init(
        id: String = UUID().uuidString,
        targetLanguage: String,
        currentLevel: String = "A1",
        levelProgress: Double = 0
    ) {
        self.id = id
        self.targetLanguage = targetLanguage
        self.currentLevel = currentLevel
        self.levelProgress = levelProgress
        self.totalStudyTime = 0
        self.totalLessons = 0
        self.totalWordsLearned = 0
        self.currentStreak = 0
        self.longestStreak = 0
        self.totalXP = 0
        self.weeklyXP = 0
        self.vocabulary = []
    }
}

// MARK: - Vocabulary Word
@Model
final class VocabularyWord {
    @Attribute(.unique) var id: String
    var word: String
    var language: String
    var translation: String
    var pronunciation: String?
    var exampleSentence: String?

    // SRS Data
    var easeFactor: Double
    var intervalDays: Int
    var repetitions: Int
    var nextReview: Date
    var lastReviewed: Date?

    // Stats
    var timesCorrect: Int
    var timesIncorrect: Int
    var masteryLevel: Double
    var isMastered: Bool

    var addedAt: Date
    var profile: LearningProfile?

    init(
        id: String = UUID().uuidString,
        word: String,
        language: String,
        translation: String,
        pronunciation: String? = nil,
        exampleSentence: String? = nil
    ) {
        self.id = id
        self.word = word
        self.language = language
        self.translation = translation
        self.pronunciation = pronunciation
        self.exampleSentence = exampleSentence
        self.easeFactor = 2.5
        self.intervalDays = 1
        self.repetitions = 0
        self.nextReview = Date()
        self.timesCorrect = 0
        self.timesIncorrect = 0
        self.masteryLevel = 0
        self.isMastered = false
        self.addedAt = Date()
    }
}

// MARK: - Study Session
@Model
final class StudySession {
    @Attribute(.unique) var id: String
    var sessionType: String // conversation, lesson, review, pronunciation
    var targetLanguage: String
    var startedAt: Date
    var endedAt: Date?
    var durationMinutes: Int
    var xpEarned: Int
    var wordsPracticed: Int
    var accuracyRate: Double?

    init(
        id: String = UUID().uuidString,
        sessionType: String,
        targetLanguage: String
    ) {
        self.id = id
        self.sessionType = sessionType
        self.targetLanguage = targetLanguage
        self.startedAt = Date()
        self.durationMinutes = 0
        self.xpEarned = 0
        self.wordsPracticed = 0
    }
}

// MARK: - Achievement
@Model
final class Achievement {
    @Attribute(.unique) var id: String
    var name: String
    var descriptionText: String
    var icon: String
    var xpReward: Int
    var isEarned: Bool
    var earnedAt: Date?

    init(
        id: String,
        name: String,
        description: String,
        icon: String,
        xpReward: Int
    ) {
        self.id = id
        self.name = name
        self.descriptionText = description
        self.icon = icon
        self.xpReward = xpReward
        self.isEarned = false
    }
}

// MARK: - API Response Models
struct TutorResponse: Codable {
    let message: String
    let corrections: [Correction]?
    let vocabulary: [VocabularyItem]?
    let grammarTips: [String]?
    let encouragement: String?
}

struct Correction: Codable, Identifiable {
    var id: String { original }
    let original: String
    let corrected: String
    let explanation: String
}

struct VocabularyItem: Codable, Identifiable {
    var id: String { word }
    let word: String
    let definition: String
    let example: String?
}

struct PronunciationResult: Codable {
    let transcript: String
    let overallScore: Double
    let accuracyScore: Double
    let fluencyScore: Double
    let wordScores: [WordScore]
    let feedback: String
    let suggestions: [String]
}

struct WordScore: Codable, Identifiable {
    var id: String { expected }
    let expected: String
    let spoken: String
    let score: Double
    let isCorrect: Bool
}

// MARK: - Lesson Models
struct Lesson: Codable, Identifiable {
    let id: String
    let language: String
    let level: String
    let title: String
    let description: String
    let category: String
    let estimatedMinutes: Int
    let xpReward: Int
    var isCompleted: Bool
    var isLocked: Bool
}

struct DailyChallenge: Identifiable {
    let id: String
    let title: String
    let target: Int
    var current: Int
    let xpReward: Int

    var isComplete: Bool {
        current >= target
    }

    var progress: Double {
        Double(current) / Double(target)
    }
}
