import SwiftUI
import AVFoundation

struct ConversationView: View {
    @EnvironmentObject var learningManager: LearningManager
    @State private var messages: [ChatMessage] = []
    @State private var inputText = ""
    @State private var isLoading = false
    @State private var isRecording = false
    @State private var selectedTopic = "general"

    let topics = [
        ("general", "일상", "💬"),
        ("travel", "여행", "✈️"),
        ("business", "비즈니스", "💼"),
        ("food", "음식", "🍽️"),
        ("culture", "문화", "🎭")
    ]

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Topic Selector
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(topics, id: \.0) { topic in
                            TopicButton(
                                id: topic.0,
                                label: topic.1,
                                icon: topic.2,
                                isSelected: selectedTopic == topic.0
                            ) {
                                selectedTopic = topic.0
                            }
                        }
                    }
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                }

                Divider()

                // Messages
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(messages) { message in
                                MessageBubble(message: message)
                            }

                            if isLoading {
                                TypingIndicator()
                            }
                        }
                        .padding()
                    }
                    .onChange(of: messages.count) { _, _ in
                        if let lastMessage = messages.last {
                            withAnimation {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                }

                Divider()

                // Input Area
                HStack(spacing: 12) {
                    // Text Field
                    TextField("메시지 입력...", text: $inputText, axis: .vertical)
                        .textFieldStyle(.plain)
                        .padding(12)
                        .background(Color(.systemGray6))
                        .clipShape(RoundedRectangle(cornerRadius: 20))
                        .lineLimit(1...4)

                    // Voice Button
                    Button {
                        toggleRecording()
                    } label: {
                        Image(systemName: isRecording ? "mic.fill" : "mic")
                            .font(.title2)
                            .foregroundStyle(isRecording ? .red : .secondary)
                            .frame(width: 44, height: 44)
                            .background(isRecording ? Color.red.opacity(0.1) : Color(.systemGray6))
                            .clipShape(Circle())
                    }

                    // Send Button
                    Button {
                        sendMessage()
                    } label: {
                        Image(systemName: "arrow.up.circle.fill")
                            .font(.title)
                            .foregroundStyle(inputText.isEmpty ? .secondary : .blue)
                    }
                    .disabled(inputText.isEmpty || isLoading)
                }
                .padding()
            }
            .navigationTitle("AI 튜터")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Button("새 대화 시작", systemImage: "plus") {
                            messages = []
                            addWelcomeMessage()
                        }
                        Button("대화 저장", systemImage: "square.and.arrow.down") {
                            // Save conversation
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .onAppear {
                if messages.isEmpty {
                    addWelcomeMessage()
                }
            }
        }
    }

    private func addWelcomeMessage() {
        let welcome = ChatMessage(
            role: .assistant,
            content: "Hello! I'm MUSE, your AI language tutor. Let's practice together! What would you like to talk about today?"
        )
        messages.append(welcome)
    }

    private func sendMessage() {
        guard !inputText.isEmpty else { return }

        let userMessage = ChatMessage(role: .user, content: inputText)
        messages.append(userMessage)
        let userInput = inputText
        inputText = ""
        isLoading = true

        // Simulate API call
        Task {
            try? await Task.sleep(nanoseconds: 1_500_000_000)

            let response = ChatMessage(
                role: .assistant,
                content: "That's a great sentence! Your English is improving. Let me give you some feedback...",
                corrections: [
                    Correction(original: "example", corrected: "Example", explanation: "Capitalize at the start of a sentence")
                ],
                vocabulary: [
                    VocabularyItem(word: "improve", definition: "to get better", example: "Your skills will improve with practice.")
                ]
            )

            await MainActor.run {
                messages.append(response)
                isLoading = false
                learningManager.addXP(5)
            }
        }
    }

    private func toggleRecording() {
        isRecording.toggle()
        // Implement speech recognition
    }
}

// MARK: - Chat Message Model
struct ChatMessage: Identifiable {
    let id = UUID()
    let role: MessageRole
    let content: String
    var corrections: [Correction]?
    var vocabulary: [VocabularyItem]?
    let timestamp = Date()

    enum MessageRole {
        case user, assistant
    }
}

// MARK: - Message Bubble
struct MessageBubble: View {
    let message: ChatMessage

    var body: some View {
        HStack {
            if message.role == .user { Spacer() }

            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 8) {
                Text(message.content)
                    .padding(12)
                    .background(message.role == .user ? Color.blue : Color(.systemGray6))
                    .foregroundStyle(message.role == .user ? .white : .primary)
                    .clipShape(RoundedRectangle(cornerRadius: 16))

                // Corrections
                if let corrections = message.corrections, !corrections.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Label("교정", systemImage: "lightbulb.fill")
                            .font(.caption)
                            .foregroundStyle(.orange)

                        ForEach(corrections) { correction in
                            VStack(alignment: .leading, spacing: 2) {
                                Text(correction.original)
                                    .strikethrough()
                                    .foregroundStyle(.secondary)
                                Text(correction.corrected)
                                    .foregroundStyle(.green)
                                Text(correction.explanation)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            .padding(8)
                            .background(Color.orange.opacity(0.1))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                        }
                    }
                }

                // Vocabulary
                if let vocabulary = message.vocabulary, !vocabulary.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Label("새 단어", systemImage: "book.fill")
                            .font(.caption)
                            .foregroundStyle(.blue)

                        ForEach(vocabulary) { word in
                            VStack(alignment: .leading, spacing: 2) {
                                Text(word.word)
                                    .fontWeight(.medium)
                                Text(word.definition)
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            .padding(8)
                            .background(Color.blue.opacity(0.1))
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                        }
                    }
                }
            }
            .frame(maxWidth: 280, alignment: message.role == .user ? .trailing : .leading)

            if message.role == .assistant { Spacer() }
        }
    }
}

// MARK: - Topic Button
struct TopicButton: View {
    let id: String
    let label: String
    let icon: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 4) {
                Text(icon)
                Text(label)
                    .font(.subheadline)
                    .fontWeight(.medium)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(isSelected ? Color.blue.opacity(0.1) : Color(.systemGray6))
            .foregroundStyle(isSelected ? .blue : .primary)
            .clipShape(Capsule())
        }
    }
}

// MARK: - Typing Indicator
struct TypingIndicator: View {
    @State private var dotCount = 0

    var body: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3) { i in
                    Circle()
                        .fill(Color.secondary)
                        .frame(width: 8, height: 8)
                        .opacity(dotCount == i ? 1 : 0.3)
                }
            }
            .padding(12)
            .background(Color(.systemGray6))
            .clipShape(RoundedRectangle(cornerRadius: 16))

            Spacer()
        }
        .onAppear {
            Timer.scheduledTimer(withTimeInterval: 0.3, repeats: true) { _ in
                dotCount = (dotCount + 1) % 3
            }
        }
    }
}

#Preview {
    ConversationView()
        .environmentObject(LearningManager())
}
