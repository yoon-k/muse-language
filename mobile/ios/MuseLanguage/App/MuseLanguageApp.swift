import SwiftUI
import SwiftData

@main
struct MuseLanguageApp: App {
    var sharedModelContainer: ModelContainer = {
        let schema = Schema([
            User.self,
            LearningProfile.self,
            VocabularyWord.self,
            StudySession.self,
            Achievement.self
        ])
        let modelConfiguration = ModelConfiguration(schema: schema, isStoredInMemoryOnly: false)

        do {
            return try ModelContainer(for: schema, configurations: [modelConfiguration])
        } catch {
            fatalError("Could not create ModelContainer: \(error)")
        }
    }()

    @StateObject private var authManager = AuthManager()
    @StateObject private var learningManager = LearningManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authManager)
                .environmentObject(learningManager)
        }
        .modelContainer(sharedModelContainer)
    }
}

// MARK: - Content View
struct ContentView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
            } else {
                OnboardingView()
            }
        }
    }
}

// MARK: - Main Tab View
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("홈", systemImage: "house.fill")
                }
                .tag(0)

            LessonsView()
                .tabItem {
                    Label("레슨", systemImage: "book.fill")
                }
                .tag(1)

            ConversationView()
                .tabItem {
                    Label("대화", systemImage: "message.fill")
                }
                .tag(2)

            VocabularyView()
                .tabItem {
                    Label("단어장", systemImage: "character.book.closed.fill")
                }
                .tag(3)

            ProfileView()
                .tabItem {
                    Label("프로필", systemImage: "person.fill")
                }
                .tag(4)
        }
        .tint(.blue)
    }
}
