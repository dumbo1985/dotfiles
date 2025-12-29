-- ========================================
-- 输入法切换模块
-- ========================================
local last_input_method = nil

-- 异步执行 system 命令，避免阻塞
local function run_async(cmd, args, callback)
	local handle
	handle = vim.loop.spawn(cmd, { args = args }, function(code, signal)
		if callback then
			callback(code, signal)
		end
		if handle then
			handle:close()
		end
	end)
end

-- 获取当前输入法（异步）
local function get_current_input_method(callback)
	local stdout = vim.loop.new_pipe(false)
	local handle
	handle = vim.loop.spawn("im-select", { stdio = { nil, stdout, nil } }, function()
		stdout:close()
		if handle then
			handle:close()
		end
	end)

	local chunks = {}
	stdout:read_start(function(err, data)
		assert(not err, err)
		if data then
			table.insert(chunks, data)
		else
			local result = table.concat(chunks):gsub("\n", "")
			if callback then
				callback(result)
			end
		end
	end)
end

-- 自动切换：进入 Insert 恢复原输入法
vim.api.nvim_create_autocmd("InsertEnter", {
	callback = function()
		if not last_input_method then
			get_current_input_method(function(method)
				last_input_method = method
			end)
		elseif last_input_method then
			run_async("im-select", { last_input_method })
		end
	end,
})

-- 自动切换：退出 Insert 统一切到英文
vim.api.nvim_create_autocmd("InsertLeave", {
	callback = function()
		run_async("im-select", { "com.apple.keylayout.ABC" })
	end,
})

-- 提供手动命令 :IMToggle
vim.api.nvim_create_user_command("IMToggle", function()
	get_current_input_method(function(method)
		if method == "com.apple.keylayout.ABC" and last_input_method then
			run_async("im-select", { last_input_method })
			vim.notify("切换到上次输入法: " .. last_input_method, vim.log.levels.INFO)
		else
			run_async("im-select", { "com.apple.keylayout.ABC" })
			vim.notify("切换到英文输入法", vim.log.levels.INFO)
		end
	end)
end, {})

