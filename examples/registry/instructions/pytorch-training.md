# PyTorch Training Expert

Use this expert for deep learning pipelines with reproducible training and evaluation, covering CNNs, RNNs, transformers, and custom architectures.

## When to use this expert
- The task requires training or fine-tuning a neural network on image, text, sequence, or tabular data.
- Mixed precision training, learning rate scheduling, or gradient clipping is needed.
- The user needs reproducible training with deterministic seeds and checkpoint recovery.
- Custom loss functions, architectures, or training loops are involved.

## Execution behavior

1. Set deterministic seeds early: `torch.manual_seed(seed)`, `torch.cuda.manual_seed_all(seed)`, `np.random.seed(seed)`, `random.seed(seed)`. Set `torch.backends.cudnn.deterministic = True` and `torch.backends.cudnn.benchmark = False` for full reproducibility, noting the performance cost.
2. Define the `Dataset` and `DataLoader` with explicit `num_workers`, `pin_memory=True` (for GPU), and a seeded `generator` for shuffling. Use `persistent_workers=True` when `num_workers > 0` to avoid repeated worker startup.
3. Build the model, loss function, and optimizer as separate, explicit blocks. Use `model.to(device)` before constructing the optimizer so parameters are on the correct device.
4. Configure a learning rate scheduler (e.g., `CosineAnnealingLR`, `OneCycleLR`, `ReduceLROnPlateau`). For `ReduceLROnPlateau`, step with the validation metric; for others, step per epoch or per batch as documented.
5. Enable mixed precision with `torch.amp.GradScaler` and `torch.amp.autocast(device_type="cuda")`. Wrap only the forward pass and loss computation in autocast; keep the backward pass and optimizer step outside.
6. Implement gradient clipping with `torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)` after `loss.backward()` and before `optimizer.step()` to stabilize training.
7. Track train and validation loss per epoch. Implement early stopping with a patience counter on the validation metric. Save the best model state with `torch.save({"epoch": e, "model_state_dict": ..., "optimizer_state_dict": ..., "best_val_loss": ...}, path)`.
8. After training, load the best checkpoint, run a final evaluation on the held-out test set, and report metrics.

## Decision tree
- If dataset fits in memory -> preload in `__init__` and transform in `__getitem__`. If too large -> use lazy loading with caching or memory-mapped files.
- If training is unstable (loss spikes) -> reduce learning rate, add gradient clipping, or check for NaN in inputs. Enable anomaly detection with `torch.autograd.set_detect_anomaly(True)` temporarily.
- If GPU memory is insufficient -> reduce batch size first, then try gradient accumulation (`accumulation_steps`), then try mixed precision, and only then consider model parallelism.
- If fine-tuning a pretrained model -> freeze early layers with `param.requires_grad = False`, use a lower learning rate for pretrained layers (differential LR), and a higher rate for the new head.
- If validation loss diverges from train loss early -> the model is overfitting. Add dropout, weight decay, data augmentation, or reduce model capacity.
- If using multi-GPU -> prefer `DistributedDataParallel` over `DataParallel` for better scaling. Initialize the process group before model wrapping.

## Anti-patterns
- NEVER call `optimizer.step()` before `loss.backward()`. The gradient buffers will be stale or zero.
- NEVER forget `optimizer.zero_grad()` (or `model.zero_grad()`) at the start of each training step. Accumulated gradients from prior batches corrupt updates.
- NEVER evaluate with the model in training mode. Always call `model.eval()` and wrap inference in `with torch.no_grad():` to disable dropout/batchnorm updates and save memory.
- NEVER move data to GPU inside the model's `forward()` method. Move inputs to device in the training loop before passing to the model.
- NEVER use `torch.save(model, path)` for production checkpoints. Save `model.state_dict()` instead, which is architecture-independent and more portable.

## Common mistakes
- Constructing the optimizer before calling `model.to(device)`, causing parameters to remain on CPU while the model is on GPU.
- Forgetting to call `scaler.update()` after `scaler.step(optimizer)` when using mixed precision, which silently disables gradient scaling.
- Using `ReduceLROnPlateau` but stepping it with the training loss instead of the validation metric, defeating its purpose.
- Setting `num_workers` too high, causing excessive memory usage or deadlocks on systems with limited shared memory.
- Not handling the `DataLoader` worker random seed, leading to identical augmentations across workers. Pass a `worker_init_fn` that seeds each worker differently.
- Loading a checkpoint without calling `model.eval()` or without restoring the optimizer state, which breaks training resumption.

## Output contract
- Record the device choice (CPU / GPU model) and precision mode (FP32 / AMP).
- Include epoch-wise metric history (train loss, val loss, learning rate) as a logged table or saved CSV.
- Save at least one recoverable checkpoint containing model state, optimizer state, epoch number, and best validation metric.
- Report final model performance on held-out validation or test data, not on training data.
- Record the PyTorch version and CUDA version used.
- If mixed precision was used, note any operations that required FP32 fallback.
- Include total training time and throughput (samples/second) when relevant.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** to prepare tabular inputs or the **OpenCV Expert** for image preprocessing pipelines.
- After this expert -> use the **Machine Learning Export Expert** to convert the trained model to ONNX or TorchScript for serving.
- After this expert -> use the **Visualization Expert** to plot training curves, confusion matrices, or attention maps.
- Related -> the **Gradient Boosting Expert** for tabular tasks where tree models may outperform neural networks with less tuning.
- Related -> the **NLP Expert** for transformer fine-tuning workflows using Hugging Face integration.
