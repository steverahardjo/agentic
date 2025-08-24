class ReactAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        description: str = "",
        memory: Optional[MemoryEngine] = InMemory,
        funcs: Optional[List[Callable]] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            memory=memory,
            funcs=funcs,
            prompt=react_prompt
        )
        self.max_iter = 5

    def run(
        self,
        user_input: str,
        llm_inst: Optional[LanguageModel] = None,
        temp: int = 0
    ):
        curr_iter = 0
        result = ""

        while curr_iter < self.max_iter:
            # Get LLM output (don’t force debug_mode=True here)
            result = super().run(
                user_input=user_input,
                llm_inst=llm_inst,
                temp=temp,
                debug_mode=False,   # use actual model
                save_mode=True
            )

            # Save in memory
            self.memory.add(self.name, result)

            # Check stopping condition
            if result.strip().startswith("[FINISHED]"):
                return result  # ✅ return immediately

            curr_iter += 1

        # Safety net if loop exits without [FINISHED]
        return f"[FAILED] Reached max iterations ({self.max_iter}) without finishing."
