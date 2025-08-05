import asyncio
import os
from platforms.code_review_platform import CodeReviewPlatform
from confrig import Config
from utils.formatters import pretty_review,create_summary
from utils.storage import save_report

async def run_review(
    platform: CodeReviewPlatform,
    code: str,
    description: str,
    review_type: str = "comprehensive",
):
    """Sends code to the platform, formats the reply, saves the report."""
    print(f"\n🚀 Starting {review_type} review …\n")
    result = await platform.review_code(code, description, review_type)

    if result.get("status") != "completed":
        print("❌ Review failed. Check logs for details.")
        return

    raw_review = result.get("review", "")
    formatted   = pretty_review(raw_review)
    summary     = create_summary(formatted)
    report_path = save_report(formatted, description, review_type)

    # ─── console output ───
    print("✅ Review completed successfully!")
    print("═" * 60)
    print("📋 EXECUTIVE SUMMARY")
    print("═" * 60)
    print(summary or "No summary available.")
    print("\n" + "═" * 60)
    print("📋 DETAILED REVIEW REPORT")
    print("═" * 60)
    print(formatted)
    print("═" * 60)
    print(f"💾 Report saved to: {report_path.resolve()}\n")

async def interactive(platforms: CodeReviewPlatform):
    print("\n📝 Paste your code below (press Ctrl+D/Ctrl+Z followed by Enter when done):")
    code_lines = [] # List to collect code lines
    try:
        while True:
            line = input()
            code_lines.append(line) # Collect each line of code
    except EOFError:
        pass

    if not code_lines:
        print("❌ No code provided. Exiting.")
        return
    code = "\n".join(code_lines)  # Join the lines into a single string
    description = input("\n📄 Enter a brief description of the code (optional): ").strip()
    if not description:
        description = "No description provided."
    print("\n🎭 Available review types: quick, comprehensive, security_focused, performance_focused")

    review_type = input("🔍 Enter the type of review you want (default: comprehensive): ").strip()
    if not review_type:
        review_type = "comprehensive"
    
    print("\n🚀 Starting the code review process...")
    print(f"\n⚙️ Running '{review_type}' review on your code...\n")

    await run_review(platforms, code, description, review_type)

   

    

async def main():
    print("🚀 Welcome to the AI Code Review & QA Platform!")
    print("🌐 Supports OpenRouter Free Models & OpenAI GPT Models")
    print("-----------------------------------------------------------------")

    try:
        api_key= Config.get_api_key()
        use_openrouter= Config.use_openrouter()
        print(f"🔑 Using {'OpenRouter Free Model' if use_openrouter else 'OpenAI GPT-4 Model'}")
        platforms = CodeReviewPlatform(api_key, use_openrouter)
       

        while True:
            print("\nOptions:")
            print("1) Paste code to review")
            print("2) Review code from file")
            print("3) Exit")
            choice = input("Choose an option [1-3]: ").strip()

            if choice== "1":
                await interactive(platforms)
            elif choice == "2":
                file_path= input("Enter the path to the code file: ").strip()
                if not os.path.exists(file_path):
                    print(f"❌ File '{file_path}' does not exist. Please check the path and try again.")
                    continue
                with open(file_path, 'r', encoding='utf-8') as file:
                    code = file.read()
                description =os.path.basename(file_path)

                await run_review(platforms, code, description)
            elif choice == "3":
                print("👋 Thank you for using the AI Code Review & QA Platform! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select a valid option (1-3).")
    except Exception as e:
        print(f"❌ startup error: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main())